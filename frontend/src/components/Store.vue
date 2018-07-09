<template>
  <v-container grid-list-lg class="storefront">
    <v-btn v-if="controls && setUp && !embedded"
           dark
           color="green"
           fab
           hover
           fixed
           right
           bottom
           @click="showNew=true"
    >
      <v-icon large>add</v-icon>
    </v-btn>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="error">
        <p>{{error}}</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <ac-product-preview
        v-for="product in growing"
        :key="product.id"
        v-if="growing !== null && setUp"
        :product="product"
      />
      <v-jumbotron v-if="setUp && is_current && (growing !== null) && (growing.length === 0)" color="grey darken-3">
        <v-container fill-height>
          <v-layout align-center>
            <v-flex>
              <h3 class="display-3">Sell your art!</h3>
              <span class="subheading">Now that you have your disbursement account set up, you can create products to sell on Artconomy.</span>
              <v-divider class="my-3" />
              <div class="mb-3"><span class="title">Create your first product now:</span></div>
              <v-btn large color="primary" class="mx-0" @click="showNew = true">New Product</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-jumbotron>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 v-if="is_current && !setUp && !embedded">
        <p>To open a store, you must first set up your
          <router-link :to="{name: 'Settings', params: {tabName: 'payment', 'username': this.viewer.username, 'subTabName': 'disbursement'}}">
            deposit account.
          </router-link>
        </p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 v-if="is_current && setUp && embedded" text-xs-center>
        <v-btn large color="primary" class="mx-0" @click="showNew = true">New Product</v-btn>
      </v-flex>
    </v-layout>
    <ac-form-dialog title="New Product" submit-text="Create" v-model="showNew"
                    ref="newProdForm" :schema="newProdSchema" :model="newProdModel"
                         :options="newProdOptions" :success="addProduct"
                         :url="`/api/sales/v1/account/${this.username}/products/`"
      />
  </v-container>
</template>

<style scoped>

</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import AcProductPreview from './ac-product-preview'
  import AcFormContainer from './ac-form-container'
  import VueFormGenerator from 'vue-form-generator'
  import { ratings, validateNonEmpty } from '../lib'
  import AcFormDialog from './ac-form-dialog'

  export default {
    name: 'Store',
    components: {
      AcFormDialog,
      AcProductPreview,
      AcFormContainer
    },
    props: ['endpoint', 'embedded'],
    mixins: [Viewer, Perms, Paginated],
    data () {
      return {
        showNew: false,
        url: this.endpoint,
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
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Hidden?',
            model: 'hidden',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'This product will not be visible on your storefront.'
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
            label: 'File',
            model: 'file',
            uniqueId: 'productFile',
            required: true,
            validator: validateNonEmpty
          },
          {
            type: 'v-file-upload',
            id: 'preview',
            label: 'Preview Image/Thumbnail',
            model: 'preview',
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
      }
    },
    computed: {
      setUp () {
        if (!this.is_current) {
          return true
        }
        return this.user.dwolla_configured
      }
    },
    watch: {
      endpoint () {
        this.url = this.endpoint
        this.fetchItems()
      }
    },
    created () {
      this.fetchItems()
    }
  }
</script>
