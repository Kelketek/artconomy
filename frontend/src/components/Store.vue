<template>
  <v-container grid-list-lg class="storefront">
    <ac-add-button text="New Product" v-model="showNew" v-if="controls && setUp && !embedded && !iFrame"></ac-add-button>
    <ac-product-list :endpoint="this.endpoint" :i-frame="iFrame" counter-name="productListCount" />
    <v-layout row wrap v-if="setUp && isCurrent && productCount === 0">
      <v-flex xs12>
        <v-card color="grey darken-3">
          <v-responsive :aspect-ratio="16/5" max-width="100%">
            <v-container fill-height>
              <v-layout align-center>
                <v-flex>
                  <h3 class="display-3">Sell your art!</h3>
                  <span class="subheading">Now that you have your payout settings configured, you can create products to sell on Artconomy.</span>
                  <v-divider class="my-3" />
                  <div class="mb-3"><span class="title">Create your first product now:</span></div>
                  <v-btn large color="primary" class="mx-0" @click="showNew = true">New Product</v-btn>
                </v-flex>
              </v-layout>
            </v-container>
          </v-responsive>
        </v-card>
      </v-flex>
    </v-layout>
    <v-layout row wrap v-if="!setUp && !embedded">
      <v-flex xs12>
        <p>To open a store, you must first set up your
          <router-link :to="{name: 'Settings', params: {tabName: 'payment', 'username': this.viewer.username, 'subTabName': 'disbursement'}}">
            payout settings.</router-link>
        </p>
      </v-flex>
    </v-layout>
    <v-layout row wrap v-if="isCurrent && setUp && embedded">
      <v-flex xs12 text-xs-center>
        <v-btn large color="primary" class="mx-0" @click="showNew = true">New Product</v-btn>
      </v-flex>
    </v-layout>
    <ac-form-dialog title="New Product" submit-text="Create" v-model="showNew"
                    ref="newProdForm" :schema="newProdSchema" :model="newProdModel"
                         :options="newProdOptions" :success="addProduct"
                         :url="`/api/sales/v1/account/${this.username}/products/`"
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
      </v-layout>
    </ac-form-dialog>
  </v-container>
</template>

<style scoped>

</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import AcProductPreview from './ac-product-preview'
  import AcFormContainer from './ac-form-container'
  import VueFormGenerator from 'vue-form-generator'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import {artCall, ratings, validateNonEmpty, EventBus} from '../lib'
  import AcFormDialog from './ac-form-dialog'
  import AcProductList from './ac-product-list'
  import AcAddButton from './ac-add-button'

  export default {
    name: 'Store',
    components: {
      AcAddButton,
      AcProductList,
      AcFormDialog,
      AcProductPreview,
      AcFormContainer
    },
    directives: {
      ObserveVisibility
    },
    props: ['endpoint', 'embedded', 'iFrame'],
    mixins: [Viewer, Perms],
    data () {
      return {
        showNew: false,
        pricing: null,
        productCount: null,
        newProdModel: {
          name: '',
          category: 0,
          description: '',
          hidden: false,
          rating: '0',
          task_weight: 1,
          favorites_hidden: false,
          revisions: 1,
          max_parallel: 0,
          expected_turnaround: 3,
          price: 0,
          tags: [],
          file: [],
          preview: []
        },
        newProdSchema: {
          fields: [{
            type: 'v-text',
            label: 'Product Name',
            model: 'name',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
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
          },
          {
            type: 'v-text',
            inputType: 'number',
            label: 'Revisions',
            model: 'revisions',
            step: '1',
            min: '0',
            hint: 'How many previews/waves of notes are offered with this piece. For instance, if you want to let the commissioner check the sketch lines before delivering a final inked piece, that would be one revision.',
            featured: true,
            required: true
          }, {
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
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Max at Once',
            model: 'max_parallel',
            step: '1',
            min: '0',
            hint: (
              'How many of this product you are willing to take on, regardless of task weight. For ' +
              'instance, if this is a full color piece, and you do sketches as well, and never want to ' +
              'take more than 2 full color pieces at a time, you could set this to 2. If this is set to ' +
              'zero, allows you to fill your entire max load with this product if that is what commissioners ' +
              'order.'
            ),
            featured: true,
            required: true
          }, {
            type: 'v-text',
            label: 'Description',
            model: 'description',
            multiLine: true,
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'tag-search',
            model: 'tags',
            label: 'Tags',
            featured: true,
            placeholder: 'Search tags',
            styleClasses: 'field-input',
            hint: 'Add some tags to make searching for your product easier, such as refsheet, inks, or watercolor.'
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Hidden?',
            model: 'hidden',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, this product will not be visible on your storefront.'
          }, {
            type: 'v-select',
            label: 'Rating',
            model: 'rating',
            featured: true,
            required: true,
            values: ratings,
            hint: 'The content rating of your preview image (even if individual commissions may vary)',
            selectOptions: {
              hideNoneSelectedText: true
            },
            validator: VueFormGenerator.validators.required
          }, {
            type: 'v-file-upload',
            id: 'file',
            label: 'Sample',
            model: 'file',
            uniqueId: 'productFile',
            required: true,
            hint: "A sample image for customers to look at",
            validator: validateNonEmpty
          },
          {
            type: 'v-file-upload',
            id: 'preview',
            label: 'Preview Image/Thumbnail',
            model: 'preview',
            hint: 'Smaller sample image seen when searching or browsing. Should be a square image. We recommend a size not smaller than 300x300 pixels.',
            required: false
          }]
        },
        newProdOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      addProduct (response) {
        this.$router.history.push(
          {name: 'Product', params: {username: this.user.username, productID: response.id}, query: {editing: true}}
        )
        this.$root.$loadUser()
      },
      setCounter (counterData) {
        if (counterData.name === 'productListCount')
        this.productCount = counterData.count
      },
      loadPricing (response) {
        this.pricing = response
      }
    },
    computed: {
      setUp () {
        if (!this.isCurrent) {
          return true
        }
        return this.user.bank_account_status
      },
      fee () {
        return ((this.price * (this.user.percentage_fee * 0.01)) + parseFloat(this.user.static_fee)).toFixed(2)
      },
      payout () {
        return (this.price - this.fee).toFixed(2)
      },
      price () {
        if (parseFloat(this.newProdModel.price + '') <= 0) {
          return 0
        }
        if (isNaN(parseFloat(this.newProdModel.price + ''))) {
          return 0
        }
        return (parseFloat(this.newProdModel.price + '')).toFixed(2)
      },
      landscapeDifference () {
        let standardFee = ((this.price * (this.pricing.standard_percentage * 0.01)) + parseFloat(this.pricing.standard_static)).toFixed(2)
        let landscapeFee = ((this.price * (this.pricing.landscape_percentage * 0.01)) + parseFloat(this.pricing.landscape_static)).toFixed(2)
        return (parseFloat(standardFee) - parseFloat(landscapeFee)).toFixed(2)
      }
    },
    created () {
      artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing)
      EventBus.$on('result-count', this.setCounter)
    }
  }
</script>
