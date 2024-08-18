<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Select a Product to invoice.</h1>
      </v-col>
    </v-row>
    <ac-paginated :list="products">
      <v-row>
        <v-col cols="12" sm="6" md="4" lg="3" v-for="product in products.list" :key="product.x!.id">
          <ac-link :to="{name: 'NewOrder', params: {username, invoiceMode: 'invoice', productId: `${product.x!.id}`}}">
            <ac-product-preview :product="product.x!" :show-username="false" :linked="false" />
          </ac-link>
        </v-col>
        <v-col cols="12" sm="6" md="4" lg="3">
          <v-card>
            <v-card-title>Custom Project</v-card-title>
            <v-card-text>
              <v-btn color="green" block @click="showCustom = true"><v-icon :icon="mdiPlus"/>Create Custom Invoice</v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </ac-paginated>
    <ac-form-dialog v-bind="customForm.bind" v-model="showCustom" @submit="customForm.submitThen(visitDeliverable)" :large="true" title="Custom invoice">
      <v-row>
        <v-col cols="12" md="6">
          <ac-bound-field
              :field="customForm.fields.buyer"
              label="Customer username/email"
              field-type="ac-user-select"
              item-value="username"
              :multiple="false"
              :allow-raw="true"
              hint="Enter the username or the email address of the customer this commission is for.
                  This can be left blank if you only want to use this order for tracking purposes."
          />
        </v-col>
        <v-col cols="6">
          <ac-bound-field
              field-type="ac-character-select" :field="customForm.fields.characters" label="Characters"
              hint="Start typing a character's name to search."
              v-if="showCharacters"
              :init-items="initCharacters"
          />
        </v-col>
        <v-col cols="12">
          <ac-bound-field
              field-type="ac-rating-field"
              :field="customForm.fields.rating"
          />
        </v-col>
        <v-col cols="12">
          <ac-bound-field
              label="Details"
              :field="customForm.fields.details"
              field-type="ac-editor"
              :save-indicator="false"
              hint="Enter any information you need to remember in order to complete this commission.
                  NOTE: This information will be visible to the buyer."
          />
        </v-col>
        <v-col cols="12">
          <ac-bound-field
              field-type="ac-uppy-file"
              uppy-id="uppy-new-order"
              :field="customForm.fields.references"
              :max-number-of-files="10"
              label="(Optional) Add some reference images!"
              :persistent-hint="true"
              :persist="true"
          />
        </v-col>
        <v-col cols="12" md="4" offset-md="4">
          <ac-bound-field
              field-type="ac-checkbox" :field="customForm.fields.hidden" label="Hidden Order"
              :persistent-hint="true"
              hint="If selected, this order's details will be hidden on your public queue (if you have your public queue enabled.)"
          />
        </v-col>
        <v-col cols="12">
          <v-alert>
            You will have the opportunity to add line items and make other adjustments on the next screen.
          </v-alert>
        </v-col>
      </v-row>
    </ac-form-dialog>
  </v-container>
</template>

<script setup lang="ts">
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {flatten, prepopulateCharacters} from '@/lib/lib.ts'
import {useList} from '@/store/lists/hooks.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import Product from '@/types/Product.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {defineAsyncComponent, ref} from 'vue'
import {Character} from '@/store/characters/types/Character.ts'
import Deliverable from '@/types/Deliverable.ts'
import {useRouter} from 'vue-router'
import {mdiPlus} from '@mdi/js'
const AcProductPreview = defineAsyncComponent(() => import('@/components/AcProductPreview.vue'))
const AcFormDialog = defineAsyncComponent(() => import('@/components/wrappers/AcFormDialog.vue'))
const AcBoundField = defineAsyncComponent(() => import('@/components/fields/AcBoundField.ts'))
const AcPaginated = defineAsyncComponent(() => import('@/components/wrappers/AcPaginated.vue'))

const props = defineProps<SubjectiveProps>()
const router = useRouter()

useSubject(props, true)

const products = useList<Product>(`${flatten(props.username)}-products`, {endpoint: `/api/sales/account/${props.username}/products/`})
products.firstRun()

const showCustom = ref(false)
const showCharacters = ref(false)
const initCharacters = ref<Character[]>([])

const customForm = useForm('custom_work', {
  endpoint: `/api/sales/account/${props.username}/create-invoice/`,
  fields: {
    buyer: {value: null},
    hidden: {value: false},
    rating: {value: 0},
    characters: {value: []},
    details: {value: ''},
    references: {value: []},
  }
})

const visitDeliverable = (deliverable: Deliverable) => {
  router.push({name: 'SaleDeliverablePayment', params: {username: props.username, orderId: deliverable.order.id, deliverableId: deliverable.id}})
}

prepopulateCharacters(customForm.fields.characters, showCharacters, initCharacters)
</script>
