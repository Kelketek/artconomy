<template>
  <v-container fluid :class="{'pa-0': !salesWaiting}">
    <v-row v-if="salesWaiting" class="justify-content fill-height"  align="center">
      <v-col cols="12" md="6" lg="4" offset-lg="2">
        <v-row class="justify-content fill-height"  align="center">
          <v-col class="grow">
            <ac-bound-field
              :field="searchForm.fields.product"
              field-type="ac-product-select"
              :multiple="false"
              :username="username"
              :init-items="productInitItems"
              v-if="showProduct"
              label="Filter by product"
              prepend-icon="shopping_bag"
            />
          </v-col>
          <v-col class="shrink">
            <ac-confirmation :action="clearWaitlist">
              <template v-slot:default="{on}">
                <v-btn class="clear-waitlist" color="red" :disabled="(!searchForm.fields.product.value) || inProgress" v-on="on">
                  <v-icon>delete</v-icon>
                </v-btn>
              </template>
              <template v-slot:confirmation-text>
                <v-col>
                  <p><strong class="danger-text">WARNING!</strong> This will cancel <strong>ALL</strong> orders in the waitlist for this
                    product, even any not shown in search due to user/email filtering.</p>
                  <p>Make sure your customers know <strong class="danger-text">why</strong> you are doing this before you do it!</p>
                </v-col>
              </template>
            </ac-confirmation>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" md="6" lg="4" class="text-center">
        <v-row class="justify-content fill-height"  align="center">
          <v-col class="grow">
            <ac-bound-field :field="searchForm.fields.q" prepend-icon="search" auto-focus
                            label="Search by username or email"
            />
          </v-col>
          <v-col class="shrink">
            <v-tooltip top>
              <template v-slot:activator="{on, attrs}">
                <v-btn v-on="on" v-bind="attrs" @click="dataMode = true"><v-icon>list</v-icon></v-btn>
              </template>
              <span>Show orders in 'list mode'.</span>
            </v-tooltip>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <ac-paginated :list="list">
      <template v-slot:default>
        <v-container fluid class="pa-0">
          <v-data-table :headers="headers" :items="orderItems" hide-default-footer v-if="dataMode" dense >
            <!-- eslint-disable vue/valid-v-slot -->
            <template v-slot:item.id="{item}">
              <router-link :to="item.default_path">#{{item.id}}</router-link>
            </template>
            <template v-slot:item.username="{item}">
              <ac-link :to="profileLink(item.buyer)">{{item.username}}</ac-link>
            </template>
          </v-data-table>
          <!-- eslint-enable vue/valid-v-slot -->
          <v-row no-gutters v-else>
            <v-col cols="12" sm="6" md="4" lg="2" v-for="order in list.list" :key="order.x.id">
              <ac-unread-marker :read="order.x.read">
                <ac-order-preview :order="order" :type="type" :username="username"></ac-order-preview>
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

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import {Prop} from 'vue-property-decorator'
import Order from '@/types/Order'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import {FormController} from '@/store/forms/form-controller'
import {RawData} from '@/store/forms/types/RawData'
import SearchField from '@/components/views/search/mixins/SearchField'
import AcBoundField from '@/components/fields/AcBoundField'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import {artCall, fallback, fallbackBoolean, flatten} from '@/lib/lib'
import Product from '@/types/Product'
import Vue from 'vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import Formatting from '@/mixins/formatting'
import AcLink from '@/components/wrappers/AcLink.vue'

@Component({
  components: {AcLink, AcConfirmation, AcUnreadMarker, AcBoundField, AcOrderPreview, AcPaginated},
})
export default class OrderList extends mixins(Subjective, SearchField, Formatting) {
  @Prop({required: true})
  public type!: string

  @Prop({required: true})
  public category!: string

  public showProduct = false
  public dataMode = false
  public inProgress = false

  public list: ListController<Order> = null as unknown as ListController<Order>
  public debouncedUpdate!: ((newData: RawData) => void)
  public searchForm: FormController = null as unknown as FormController
  public productInitItems: Product[] = []

  public get headers() {
    return [
      {value: 'id', text: 'ID'},
      {value: 'product_name', text: 'Product'},
      {value: 'username', text: 'User'},
      {value: 'created_on', text: 'Placed on'},
      {value: 'activity', text: 'New Activity'},
    ]
  }

  public get orderItems() {
    return this.list.list.map((x) => {
      const order = x.x as Order
      return {
        id: order.id,
        product_name: order.product_name,
        activity: (!order.read) ? '*' : '',
        username: order.buyer ? this.deriveDisplayName(order.buyer.username) : '(Pending)',
        created_on: this.formatDateTime(order.created_on),
        default_path: order.default_path,
        buyer: order.buyer,
      }
    })
  }

  public populateProduct() {
    artCall({
      url: `/api/sales/v1/account/${this.username}/products/${this.searchForm.fields.product.value}/`,
      method: 'get',
    }).then((response: Product) => {
      Vue.set(this, 'productInitItems', [response])
    }).finally(() => {
      this.showProduct = true
    })
  }

  public get salesWaiting() {
    return (this.type === 'sales') && (this.category === 'waiting')
  }

  public clearWaitlist() {
    this.inProgress = true
    artCall({
      url: `/api/sales/v1/account/${this.username}/products/${this.searchForm.fields.product.value}/clear-waitlist/`,
      method: 'post',
    }).then(() => {
      this.list.reset()
    }).finally(() => {
      this.inProgress = false
    })
  }

  public created() {
    this.searchForm = this.$getForm('waitlistSearch', {
      endpoint: '#',
      fields: {
        q: {value: ''},
        product: {value: null, omitIf: null},
        size: {value: 24},
        page: {value: 1},
      },
    })
    this.searchForm.fields.q.update(fallback(this.$route.query, 'q', ''))
    this.searchForm.fields.product.update(fallbackBoolean(this.$route.query, 'product', null))
    if (this.searchForm.fields.product.value) {
      this.populateProduct()
    } else {
      this.showProduct = true
    }
    this.list = this.$getList(`orders__${flatten(this.username)}__${this.type}__${this.category}`, {
      endpoint: `/api/sales/v1/account/${this.username}/${this.type}/${this.category}/`,
    })
  }
}
</script>
