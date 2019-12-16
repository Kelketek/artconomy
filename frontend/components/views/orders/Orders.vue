<template>
  <v-container>
    <ac-load-section v-if="isSales" :controller="stats">
      <template v-slot:default>
        <v-row no-gutters class="text-center"   >
          <v-col cols="12" md="6">
            <h1>
              <router-link style="text-decoration: underline;"
                           :to="{name: 'BuyAndSell', params: {question: 'awoo-workload-management'}}">
                AWOO
              </router-link>
              Panel
            </h1>
            <v-row no-gutters  >
              <v-col cols="6">Max Load:</v-col>
              <v-col cols="6">{{stats.x.max_load}}</v-col>
              <v-col cols="6">Current Load:</v-col>
              <v-col cols="6">{{stats.x.load}}</v-col>
              <v-col cols="6">Active Orders:</v-col>
              <v-col cols="6">{{stats.x.active_orders}}</v-col>
              <v-col cols="6">New Orders:</v-col>
              <v-col cols="6">{{stats.x.new_orders}}</v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="6" v-if="closed">
            <strong>You are currently unable to take new commissions because:</strong>
            <ul>
              <li v-if="stats.x.commissions_closed">You have set your 'commissions closed' setting.</li>
              <li v-if="stats.x.load >= stats.x.max_load">You have met or exceeded your maximum load. You can increase your
                maximum load setting to take on more commissions at one time.
              </li>
              <li v-else-if="stats.x.products_available === 0">You have no products available for customers to purchase. This
                may mean there are none, they are hidden, they have reached their 'Max at Once' level, or you do not have
                enough load remaining to take any of your existing products on.
              </li>
              <li v-if="stats.x.commissions_disabled && stats.x.new_orders">You have outstanding new orders to process. Please
                accept or reject the outstanding orders. Outstanding orders must be handled before you are opened up for new
                commissions.
              </li>
            </ul>
          </v-col>
          <v-col v-else>
            You are currently able to take commissions.
            <router-link :to="{name: 'Store', params: {username}}">Manage your store here.</router-link>
          </v-col>
        </v-row>
      </template>
    </ac-load-section>
    <v-tabs fixed-tabs>
      <v-tab :to="{name: 'Current' + baseName, params: {username}}">Current</v-tab>
      <v-tab :to="{name: 'Archived' + baseName, params: {username}}">Archived</v-tab>
      <v-tab v-if="!isCases" :to="{name: 'Cancelled' + baseName, params: {username}}">Cancelled</v-tab>
    </v-tabs>
    <v-tabs-items>
      <router-view :key="$route.path"></router-view>
    </v-tabs-items>
    <ac-add-button v-if="isSales" v-model="showNewInvoice">Create Invoice</ac-add-button>
    <ac-form-dialog v-bind="newInvoice.bind" @submit.prevent="newInvoice.submitThen(goToOrder)" v-model="showNewInvoice" :large="true" title="Issue new Invoice">
      <v-row no-gutters  >
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-bound-field
            :field="newInvoice.fields.product"
            field-type="ac-product-select"
            :multiple="false"
            label="Product"
            hint="Optional: Specify which of your product this invoice is for. This can help with organization.
                  If no product is specified, this will be considered a custom order."
            :persistent-hint="true"
          ></ac-bound-field>
        </v-col>
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-price-preview :price="newInvoice.fields.price.value" :escrow="!escrowDisabled" :username="username"></ac-price-preview>
        </v-col>
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-bound-field
            :field="newInvoice.fields.price"
            field-type="ac-price-field"
            label="Total Price"
          ></ac-bound-field>
        </v-col>
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-bound-field
            label="Customer username/email"
            :field="newInvoice.fields.buyer"
            field-type="ac-user-select"
            item-value="username"
            :multiple="false"
            :allow-raw="true"
            hint="Enter the username or the email address of the customer this commission is for.
                  This can be left blank if you only want to use this order for tracking purposes."
          />
        </v-col>
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-bound-field field-type="v-checkbox"
                          label="Paid"
                          :field="newInvoice.fields.paid"
                          hint="If the commissioner has already paid, and you just want to track this order,
                                please check this box."
                          :persistent-hint="true"
          />
        </v-col>
        <v-col class="pa-2" cols="12" sm="6" >
          <ac-bound-field field-type="v-checkbox"
                          label="Already Complete"
                          :field="newInvoice.fields.completed"
                          hint="If you have already completed the commission you're invoicing, please check this box."
                          :persistent-hint="true"
          />
        </v-col>
        <v-col class="pa-2" cols="12" sm="4" >
          <ac-bound-field
            label="Slots taken"
            :field="newInvoice.fields.task_weight"
            :persistent-hint="true"
            :disabled="newInvoice.fields.completed.value"
            hint="How many of your slots this commission will take up."
          />
        </v-col>
        <v-col class="pa-2" cols="12" sm="4" >
          <ac-bound-field
            label="Revisions included"
            :field="newInvoice.fields.revisions"
            :persistent-hint="true"
            :disabled="newInvoice.fields.completed.value"
            hint="The total number of times the buyer will be able to ask for revisions.
                  This does not include the final, so if there are no revisions, set this to zero."
            />
        </v-col>
        <v-col class="pa-2" cols="12" sm="4" >
          <ac-bound-field
            label="Expected turnaround (days)"
            :field="newInvoice.fields.revisions"
            :persistent-hint="true"
            :disabled="newInvoice.fields.completed.value"
            hint="The total number of business days you expect this task will take."
          />
        </v-col>
        <v-col class="pa-1" cols="12" >
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
    </ac-form-dialog>
  </v-container>
</template>

<script lang="ts">
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import Component, {mixins} from 'vue-class-component'
import Subjective from '../../../mixins/subjective'
import AcPaginated from '../../wrappers/AcPaginated.vue'
import {Prop, Watch} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import CommissionStats from '@/types/CommissionStats'
import {FormController} from '@/store/forms/form-controller'
import AcAddButton from '@/components/AcAddButton.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import Product from '@/types/Product'
import AcPricePreview from '@/components/AcPricePreview.vue'
import Order from '@/types/Order'
@Component({
  components: {AcPricePreview, AcBoundField, AcFormDialog, AcAddButton, AcPaginated, AcLoadSection},
})
export default class Orders extends mixins(Subjective) {
  public stats: SingleController<CommissionStats> = null as unknown as SingleController<CommissionStats>
  @Prop({required: true})
  public baseName!: string
  public showNewInvoice = false
  public newInvoice: FormController = null as unknown as FormController
  public invoiceProduct: SingleController<Product> = null as unknown as SingleController<Product>

  @Watch('newInvoice.fields.product.value')
  public updateProduct(val: undefined|null|number) {
    if (val === undefined) {
      return
    }
    if (!val) {
      this.invoiceProduct.kill()
      this.invoiceProduct.setX(null)
      return
    }
    this.invoiceProduct.endpoint = `/api/sales/v1/account/${this.username}/products/${val}/`
    this.invoiceProduct.kill()
    this.invoiceProduct.get()
  }

  @Watch('invoiceProduct.x', {deep: true})
  public updatePrice(val: Product|null) {
    if (!val) {
      return
    }
    this.newInvoice.fields.price.update(val.price)
    this.newInvoice.fields.task_weight.update(val.task_weight)
    this.newInvoice.fields.revisions.update(val.revisions)
    this.newInvoice.fields.expected_turnaround.update(val.expected_turnaround)
  }

  @Watch('invoiceProduct.x.task_weight')
  public updateWeight(val: number|undefined) {
    if (val === undefined) {
      return
    }
    this.newInvoice.fields.task_weight.update(val)
  }

  public goToOrder(order: Order) {
    this.$router.push({name: 'Sale', params: {username: this.username, orderId: order.id + ''}})
  }

  public get price() {
    if (this.invoiceProduct.x) {
      return this.invoiceProduct.x.price
    }
    return this.newInvoice.fields.price.value
  }

  public get adjustment() {
    if (!this.invoiceProduct.x) {
      return 0
    }
    return this.newInvoice.fields.price.value - this.invoiceProduct.x.price
  }

  public get isSales() {
    return this.baseName === 'Sales'
  }

  public get isCases() {
    return this.baseName === 'Cases'
  }

  public get isCurrentRoute() {
    return this.$route.name === this.baseName
  }

  public get closed() {
    const stats = this.stats.x as CommissionStats
    if (!stats) {
      return
    }
    return stats.commissions_closed || stats.commissions_disabled || stats.load >= stats.max_load
  }

  public get escrowDisabled() {
    if (!this.subjectHandler.artistProfile.x) {
      return true
    }
    if (this.newInvoice.fields.paid.value) {
      return true
    }
    return this.subjectHandler.artistProfile.x.escrow_disabled
  }

  public created() {
    const type = this.baseName.toLocaleLowerCase()
    this.invoiceProduct = this.$getSingle('invoiceProduct', {endpoint: ''})
    this.stats = this.$getSingle(`stats__sales__${this.username}`, {
      endpoint: `/api/sales/v1/account/${this.username}/sales/stats/`,
    })
    this.$listenForList(`orders__${this.username}__${type}__archived`)
    this.$listenForList(`orders__${this.username}__${type}__current`)
    if (this.isCurrentRoute) {
      this.$router.replace({name: 'Current' + this.baseName, params: {username: this.username}})
    }
    if (this.isSales) {
      this.stats.get()
      this.subjectHandler.artistProfile.get()
    }
    this.newInvoice = this.$getForm('newInvoice', {
      endpoint: `/api/sales/v1/account/${this.username}/create-invoice/`,
      fields: {
        product: {value: null},
        buyer: {value: ''},
        price: {value: 25},
        completed: {value: false},
        task_weight: {value: 0},
        revisions: {value: 1},
        private: {value: false},
        details: {value: ''},
        paid: {value: false},
        expected_turnaround: {value: 1},
      },
    })
  }
}
</script>
