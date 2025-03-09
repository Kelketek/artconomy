<template>
  <v-row class="ac-invoice-form">
    <v-col cols="12" sm="6">
      <ac-bound-field
          :field="newInvoice.fields.product"
          field-type="ac-product-select"
          :multiple="false"
          :username="username"
          label="Product"
          hint="Optional: Specify which of your product this invoice is for. This can help with organization.
                  If no product is specified, this will be considered a custom order."
          :persistent-hint="true"
      />
    </v-col>
    <slot name="second">
    </slot>
    <v-row>
      <v-col cols="12">
        <v-divider />
      </v-col>
      <v-col cols="12" md="6">
        <v-row>
          <v-col cols="12">
            <ac-bound-field
                :field="newInvoice.fields.price"
                field-type="ac-price-field"
                label="Total Price"
            />
          </v-col>
          <v-col cols="12">
            <ac-bound-field
                :field="newInvoice.fields.cascade_fees"
                field-type="ac-checkbox"
                label="Absorb Fees"
                :false-value="false"
                :persistent-hint="true"
                hint="If turned on, the price you set is the price your commissioner will see, and you
              will pay all fees from that price. If turned off, the price you set is the amount you
              take home, and the total the customer pays includes the fees."
            />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" sm="6">
        <ac-price-preview :lineItems="lineItems" :escrow="escrowEnabled" :username="username"/>
      </v-col>
    </v-row>
    <v-col cols="12" sm="4" offset-sm="4">
      <ac-bound-field field-type="ac-checkbox"
                      label="Hold for Edit"
                      :disabled="newInvoice.fields.paid.model"
                      :field="newInvoice.fields.hold"
                      hint="If you want to edit the line items on this invoice before sending it for payment, check this box."
                      :persistent-hint="true"
      />
    </v-col>
    <v-col cols="12">
      <ac-bound-field
          field-type="ac-rating-field"
          :field="newInvoice.fields.rating"
      />
    </v-col>
    <v-col cols="12" sm="4">
      <ac-bound-field
          label="Slots taken"
          :field="newInvoice.fields.task_weight"
          :persistent-hint="true"
          hint="How many of your slots this commission will take up."
      />
    </v-col>
    <v-col cols="12" sm="4">
      <ac-bound-field
          label="Revisions included"
          :field="newInvoice.fields.revisions"
          :persistent-hint="true"
          hint="The total number of times the buyer will be able to ask for revisions.
                  This does not include the final, so if there are no revisions, set this to zero."
      />
    </v-col>
    <v-col cols="12" sm="4">
      <ac-bound-field
          label="Expected turnaround (days)"
          :field="newInvoice.fields.expected_turnaround"
          :persistent-hint="true"
          hint="The total number of business days you expect this task will take."
      />
    </v-col>
    <v-col cols="12">
      <ac-bound-field
          label="description"
          :field="newInvoice.fields.details"
          field-type="ac-editor"
          :save-indicator="false"
          hint="Enter any information you need to remember in order to complete this commission.
                  NOTE: This information will be visible to the buyer."
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {FormController} from '@/store/forms/form-controller.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPricePreview from '../../price_preview/AcPricePreview.vue'
import {ListController} from '@/store/lists/controller.ts'
import type {LineItem} from '@/types/main'

defineProps<{newInvoice: FormController, escrowEnabled: boolean, lineItems: ListController<LineItem>, username: string}>()
</script>
