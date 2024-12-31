<template>
  <v-container fluid :class="{'pa-0': !salesWaiting}">
    <v-row v-if="salesWaiting" class="justify-content fill-height" align="center">
      <v-col cols="12" md="6" lg="4" offset-lg="2">
        <v-row class="justify-content fill-height" align="center">
          <div class="flex-grow-1">
            <ac-bound-field
                :field="searchForm.fields.product"
                field-type="ac-product-select"
                :multiple="false"
                :username="username"
                :init-items="productInitItems"
                :immediate-search="true"
                v-if="showProduct"
                label="Filter by product"
                :prepend-icon="mdiShopping"
            />
          </div>
          <div class="flex-shrink-0">
            <ac-confirmation :action="clearWaitlist">
              <template v-slot:default="{on}">
                <v-btn class="clear-waitlist ml-2" color="red" :disabled="(!searchForm.fields.product.value) || inProgress"
                       v-on="on" aria-label="Clear waitlist"
                >
                  <v-icon :icon="mdiDelete"/>
                </v-btn>
              </template>
              <template v-slot:confirmation-text>
                <v-col>
                  <p><strong class="danger-text">WARNING!</strong> This will cancel <strong>ALL</strong> orders in the
                    waitlist for this
                    product, even any not shown in search due to user/email filtering.</p>
                  <p>Make sure your customers know <strong class="danger-text">why</strong> you are doing this before
                    you do it!</p>
                </v-col>
              </template>
            </ac-confirmation>
          </div>
        </v-row>
      </v-col>
      <v-col cols="12" md="6" lg="4" class="text-center">
        <v-row class="justify-content fill-height" align="center">
          <div class="flex-grow-1">
            <ac-bound-field :field="searchForm.fields.q" :prepend-icon="mdiMagnify" auto-focus
                            label="Search by username or email"
            />
          </div>
          <div class="flex-shrink-0">
            <v-tooltip top>
              <template v-slot:activator="{props}">
                <v-btn v-bind="props" @click="dataMode = true">
                  <v-icon :icon="mdiListBox"/>
                </v-btn>
              </template>
              <span>Show orders in 'list mode'.</span>
            </v-tooltip>
          </div>
        </v-row>
      </v-col>
    </v-row>
    <ac-paginated :list="list" :track-pages="true">
      <template v-slot:default>
        <v-container fluid class="pa-0">
          <v-data-table :headers="headers" :items="orderItems" hide-default-footer v-if="dataMode" dense>
            <!-- eslint-disable vue/valid-v-slot -->
            <template v-slot:item.id="{item}">
              <router-link :to="item.default_path">#{{ item.id }}</router-link>
            </template>
            <template v-slot:item.username="{item}">
              <ac-link :to="profileLink(item.buyer)">{{ item.username }}</ac-link>
            </template>
          </v-data-table>
          <!-- eslint-enable vue/valid-v-slot -->
          <v-row no-gutters v-else>
            <v-col cols="12" sm="6" md="4" lg="2" v-for="order in list.list" :key="order.x!.id">
              <ac-unread-marker :read="order.x!.read">
                <ac-order-preview :order="order" :type="type" :username="username"/>
              </ac-unread-marker>
            </v-col>
          </v-row>
        </v-container>
      </template>
    </ac-paginated>
  </v-container>
</template>

<style scoped>
.danger-text {
  background-color: red;
  padding-left: 3px;
  padding-right: 3px;
  border-radius: 3px;
}
</style>

<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import {artCall, fallback, fallbackBoolean, flatten} from '@/lib/lib.ts'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {computed, ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useRoute} from 'vue-router'
import {useList} from '@/store/lists/hooks.ts'
import {deriveDisplayName, formatDateTime} from '@/lib/otherFormatters.ts'
import {mdiDelete, mdiListBox, mdiMagnify, mdiShopping} from '@mdi/js'
import {profileLink} from '@/lib/otherFormatters.ts'
import type {Order, Product, SubjectiveProps} from '@/types/main'
import {useSearchList} from '@/components/views/search/mixins/SearchList.ts'

declare interface OrderListProps {
  type: string,
  category: string,
}

const props = defineProps<OrderListProps & SubjectiveProps>()
const route = useRoute()
const showProduct = ref(false)
const dataMode = ref(false)
const inProgress = ref(false)
const productInitItems = ref<Product[]>([])

const populateProduct = () => {
  artCall({
    url: `/api/sales/account/${props.username}/products/${searchForm.fields.product.value}/`,
    method: 'get',
  }).then((response: Product) => {
    productInitItems.value = [response]
  }).finally(() => {
    showProduct.value = true
  })
}
const searchForm = useForm('waitlistSearch', {
  endpoint: '#',
  fields: {
    q: {value: ''},
    product: {
      value: null,
      omitIf: null,
    },
    size: {value: 24},
    page: {value: 1},
  },
})
searchForm.fields.q.update(fallback(route.query, 'q', ''))
searchForm.fields.product.update(fallbackBoolean(route.query, 'product', null))
if (searchForm.fields.product.value) {
  populateProduct()
} else {
  showProduct.value = true
}
const list = useList<Order>(`orders__${flatten(props.username)}__${props.type}__${props.category}`, {
  endpoint: `/api/sales/account/${props.username}/${props.type}/${props.category}/`,
})
useSearchList(searchForm, list)
const headers = [
  {
    value: 'id',
    title: 'ID',
  },
  {
    value: 'product_name',
    title: 'Product',
  },
  {
    value: 'username',
    title: 'User',
  },
  {
    value: 'created_on',
    title: 'Placed on',
  },
  {
    value: 'activity',
    title: 'New Activity',
  },
]

const orderItems = computed(() => list.list.map((x) => {
  const order = x.x as Order
  return {
    id: order.id,
    product_name: order.product_name,
    activity: (!order.read) ? '*' : '',
    username: order.buyer ? deriveDisplayName(order.buyer.username) : '(Pending)',
    created_on: formatDateTime(order.created_on),
    default_path: order.default_path,
    buyer: order.buyer,
  }
}))

const salesWaiting = computed(() => {
  return (props.type === 'sales') && (props.category === 'waiting')
})

const clearWaitlist = async () => {
  inProgress.value = true
  return artCall({
    url: `/api/sales/account/${props.username}/products/${searchForm.fields.product.value}/clear-waitlist/`,
    method: 'post',
  }).then(() => {
    list.reset()
  }).finally(() => {
    inProgress.value = false
  })
}
</script>
