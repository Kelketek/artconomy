<template>
  <div class="order-list">
    <v-layout row wrap text-xs-center v-if="stats && !buyer" class="mt-2 mb-2">
      <v-flex xs12 md6>
        <h1>
          <router-link style="text-decoration: underline;" :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'awoo-workload-management'}}">AWOO</router-link> Panel
        </h1>
        <v-layout row wrap>
          <v-flex xs6>Max Load:</v-flex>
          <v-flex xs6>{{stats.max_load}}</v-flex>
          <v-flex xs6>Current Load:</v-flex>
          <v-flex xs6>{{stats.load}}</v-flex>
          <v-flex xs6>Active Orders:</v-flex>
          <v-flex xs6>{{stats.active_orders}}</v-flex>
          <v-flex xs6>New Orders:</v-flex>
          <v-flex xs6>{{stats.new_orders}}</v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs12 md6 v-if="closed">
        <strong>You are currently unable to take new commisions because:</strong>
        <ul>
          <li v-if="stats.commissions_closed">You have set your 'commissions closed' setting.</li>
          <li v-if="stats.load >= stats.max_load">You have met or exceeded your maximum load. You can increase your maximum load setting to take on more commissions at one time.</li>
          <li v-else-if="stats.products_available === 0">You have no products available for customers to purchase. This may mean there are none, they are hidden, they have reached their 'Max at Once' level, or you do not have enough load remaining to take any of your existing products on.</li>
          <li v-if="stats.commissions_disabled && stats.new_orders">You have outstanding new orders to process. Please accept or reject the outstanding orders. Outstanding orders must be handled before you are opened up for new commissions.</li>
        </ul>
      </v-flex>
      <v-flex v-else>
        You are currently able to take commissions.
          <router-link :to="{name: 'Store', params: {username: this.username}}">Manage your store here.</router-link>
      </v-flex>
    </v-layout>
    <v-tabs v-model="tab" fixed-tabs>
      <v-tab href="#tab-current" key="current">
        <v-icon>list</v-icon>&nbsp;Current
      </v-tab>
      <v-tab href="#tab-archived" key="archived">
        <v-icon>archive</v-icon>&nbsp;Archived
      </v-tab>
      <v-tab href="#tab-cancelled" key="cancelled">
        <v-icon>do_not_disturb</v-icon>&nbsp;Cancelled
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item id="tab-current" v-if="buyer">
        <ac-order-list :url="`${url}current/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-current" v-else>
        <v-tabs v-model="currentTab" fixed-tabs>
          <v-tab href="#tab-store">Store</v-tab>
          <v-tab href="#tab-placeholders">Placeholders</v-tab>
        </v-tabs>
        <v-tabs-items v-model="currentTab">
          <v-tab-item id="tab-store">
            <ac-order-list :url="`${url}current/`" :buyer="buyer" :username="username" />
          </v-tab-item>
          <v-tab-item id="tab-placeholders" :class="{'tab-shown': shownTab('tab-placeholders')}">
            <ac-placeholder-list :url="`${url}current/placeholders/`" :username="username" />
          </v-tab-item>
        </v-tabs-items>
      </v-tab-item>
      <v-tab-item id="tab-archived" v-if="buyer">
        <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
      </v-tab-item>
      <v-tab-item id="tab-archived" v-else>
        <v-tabs v-model="archiveTab" fixed-tabs>
          <v-tab href="#tab-store">Store</v-tab>
          <v-tab href="#tab-placeholders">Placeholders</v-tab>
        </v-tabs>
        <v-tabs-items v-model="archiveTab">
          <v-tab-item id="tab-store">
            <ac-order-list :url="`${url}archived/`" :buyer="buyer" :username="username" />
          </v-tab-item>
          <v-tab-item id="tab-placeholders">
            <ac-placeholder-list :url="`${url}archived/placeholders/`" :username="username" />
          </v-tab-item>
        </v-tabs-items>
      </v-tab-item>
      <v-tab-item id="tab-cancelled">
        <ac-order-list :url="`${url}cancelled/`" :buyer="buyer" :username="username" />
      </v-tab-item>
    </v-tabs-items>
    <ac-add-button text="New Invoice" v-model="showNew" v-if="!buyer && !user.escrow_disabled"></ac-add-button>
    <ac-form-dialog title="New Invoice" submit-text="Issue" v-model="showNew"
                    ref="newInvoiceForm" :schema="newInvoiceSchema" :model="newInvoiceModel"
                    :options="newInvoiceOptions"
                    :success="visitSale"
                    url="/api/sales/v1/create-invoice/"
    >
      <v-layout slot="header">
        <v-flex text-xs-center v-if="price && !user.escrow_disabled" xs6 md3 offset-md3>
          <strong>Price: ${{price}}</strong> <br />
          Artconomy service fee: -${{ fee }} <br />
          <strong>Your payout: ${{ payout }}</strong> <br />
        </v-flex>
        <v-flex v-if="price && pricing && !user.escrow_disabled" text-xs-center xs6 md3>
          <div v-if="!landscape">
            You'll earn <strong>${{landscapeDifference}}</strong> more from this commission if you upgrade to Artconomy Landscape!
            <br />
            <v-btn :to="{name: 'Upgrade'}" color="purple">Upgrade Now!</v-btn>
          </div>
          <div v-else>
            Your Landscape subscription earns you <strong>${{landscapeDifference}}</strong> more than you would have earned on this commission otherwise!
          </div>
        </v-flex>
        <v-flex text-xs-center xs12>
          <h3>All orders are bound by the <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link></h3>
        </v-flex>
      </v-layout>
    </ac-form-dialog>
  </div>
</template>

<style>
  h3 a {
    text-decoration: underline;
  }
</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcOrderPreview from './ac-order-preview'
  import { paramHandleMap, EventBus, artCall } from '../lib'
  import AcOrderList from './ac-order-list'
  import AcPlaceholderList from './ac-placeholder-list'
  import AcAddButton from './ac-add-button'
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'Orders',
    mixins: [Viewer, Perms],
    components: {
      AcFormDialog,
      AcAddButton,
      AcPlaceholderList,
      AcOrderList,
      AcOrderPreview
    },
    data () {
      return {
        // Used by tab mapper
        query: null,
        stats: null,
        showNew: false,
        pricing: null,
        newInvoiceModel: {
          product: null,
          buyer: '',
          price: 0,
          completed: false,
          details: '',
          task_weight: 0,
          expected_turnaround: 0,
          private: false,
        },
        newInvoiceOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      shownTab (tabName) {
        if (tabName === this.currentTab && this.tab === 'tab-current') {
          EventBus.$emit('tab-shown', tabName)
          return true
        }
      },
      visitSale (response) {
        this.$router.push({name: 'Sale', params: {orderID: response.id, username: this.username}})
      },
      loadPricing (response) {
        this.pricing = response
      },
      setStats (response) {
        this.stats = response
      },
      refreshStats () {
        if (this.buyer) {
          return
        }
        artCall(`${this.url}stats/`, 'GET', undefined, this.setStats)
      },
      populatePresets (products) {
        if (!products[0]) {
          return
        }
        let product = products[0]
        this.newInvoiceModel.price = product.price
        this.newInvoiceModel.task_weight = product.task_weight
        this.newInvoiceModel.expected_turnaround = product.expected_turnaround
      }
    },
    created () {
      EventBus.$on('refresh-sales-stats', this.refreshStats)
      EventBus.$on('products-selected-product', this.populatePresets)
      artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing)
      this.refreshStats()
    },
    props: ['url', 'buyer'],
    computed: {
      tab: paramHandleMap('tabName', ['subTabName'], undefined, 'tab-current'),
      currentTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      archiveTab: paramHandleMap('subTabName', undefined, ['tab-store', 'tab-placeholders'], 'tab-store'),
      extended () {
        return this.url.indexOf('sales') !== -1
      },
      closed () {
        return this.stats.commissions_closed || this.stats.commissions_disabled || this.stats.load >= this.stats.max_load
      },
      fee () {
        return ((this.price * (this.user.percentage_fee * 0.01)) + parseFloat(this.user.static_fee)).toFixed(2)
      },
      payout () {
        return (this.price - this.fee).toFixed(2)
      },
      price () {
        if (parseFloat(this.newInvoiceModel.price + '') <= 0) {
          return 0
        }
        if (isNaN(parseFloat(this.newInvoiceModel.price + ''))) {
          return 0
        }
        return (parseFloat(this.newInvoiceModel.price + '')).toFixed(2)
      },
      landscapeDifference () {
        let standardFee = ((this.price * (this.pricing.standard_percentage * 0.01)) + parseFloat(this.pricing.standard_static)).toFixed(2)
        let landscapeFee = ((this.price * (this.pricing.landscape_percentage * 0.01)) + parseFloat(this.pricing.landscape_static)).toFixed(2)
        return (parseFloat(standardFee) - parseFloat(landscapeFee)).toFixed(2)
      },
      newInvoiceSchema () {
        let schema = {
          fields: [
            {
              type: 'product-search',
              model: 'product',
              label: 'Product',
              hint: 'Select a product to base this invoice off of. When the piece is complete, ' +
                'if the customer uploads the result and makes it public, the piece will be counted as a sample for ' +
                'this product.'
            },
            {
              type: 'user-search',
              model: 'buyer',
              label: 'Customer',
              emailPermitted: true,
              hint: 'Enter an Artconomy username, or the email address of the customer. Click/tap a user to add them.',
            },
            {
              type: 'v-text',
              label: 'Details',
              model: 'details',
              multiLine: true,
              featured: true,
              required: true,
              hint: (
                'Write down all the details you will need to complete this piece. Please note the customer will be able to see this information.'
              )
            },
            {
              type: 'v-text',
              inputType: 'number',
              label: 'Price (USD)',
              model: 'price',
              step: '.01',
              min: '1.10',
              featured: true,
              required: true
            }]
        }
        if (!this.newInvoiceModel.completed) {
          schema.fields.push.apply(schema.fields,
            [{
              type: 'v-text',
              inputType: 'number',
              label: 'Expected Turnaround (days)',
              model: 'expected_turnaround',
              step: '1',
              min: '1',
              hint: (
                'How many days you expect this piece to take from the time you approve the final order to ' +
                'delivery. Bear in mind your average work load and how long it takes for you to finish other pieces ' +
                'before starting a new one. If a piece takes 20% more days than specified, the commissioner ' +
                'may file for dispute. Completing tasks on or ahead of schedule results in improved statistics, which ' +
                'commissioners can factor into purchases.'
              ),
              featured: true,
              required: true
            }, {
              type: 'v-text',
              inputType: 'number',
              label: 'Task Weight',
              model: 'task_weight',
              step: '1',
              min: '1',
              hint: (
                'How much this product contributes to your "max load" (configurable in your settings). If you have a ' +
                'max load of 10, and a task weight of 2, you could take up to five of these at a time. This product ' +
                'will be hidden if its task weight would put you over your max load.'
              ),
              featured: true,
              required: true
            }]
          )
        }
        schema.fields.push({
          type: 'v-checkbox',
          label: 'Completed',
          model: 'completed',
          hint: 'Check this if the piece you are invoicing for has already been completed. This will ' +
            'prevent it from affecting your load.'
        }, {
          type: 'v-checkbox',
          label: 'Private Order',
          model: 'private',
          hint: 'Check this if your customer has requested this be a private order. This will prevent some ' +
            'notifications and confers some expectations under the commission agreement.'
        })
        return schema
      }
    }
  }
</script>

<style>
  @keyframes delay-display {
    0% { opacity: 0 }
    99% { opacity: 0 }
    100% { opacity: 1 }
  }
  .order-list .btn--floating {
    visibility: hidden;
    opacity: 0;
    transition: none;
  }
  .order-list .tab-shown .btn--floating {
    visibility: visible;
    opacity: 1;
    animation: delay-display 1s;
  }
</style>