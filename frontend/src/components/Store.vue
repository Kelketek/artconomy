<template>
  <div class="storefront container">
    <div class="row">
      <ac-product-preview
        v-for="product in growing"
        :key="product.id"
        v-if="growing !== null && setUp"
        :product="product"
      ></ac-product-preview>
      <div class="col-sm-12" v-if="is_current && !setUp">
        <p>To open a store, you must first set up your
          <router-link :to="{name: 'Settings', params: {tabName: 'payment', 'username': this.viewer.username}}">
            deposit account.
          </router-link>
        </p>
      </div>
    </div>
    <div class="row-centered" v-if="controls">
      <div class="col-sm-12 pt-3 col-md-4 col-centered text-center">
        <div v-if="showNew">
          <form>
            <ac-form-container ref="newProdForm" :schema="newProdSchema" :model="newProdModel"
                               :options="newProdOptions" :success="addProduct"
                               :url="`/api/sales/v1/${this.username}/products/`"
            >
              <b-button @click="showNew = false;">Cancel</b-button>
              <b-button type="submit" variant="primary" @click.prevent="$refs.newProdForm.submit">Create</b-button>
            </ac-form-container>
          </form>
        </div>
        <b-button v-else variant="primary" size="lg" @click="showNew=true" id="new-char-button">Add a new product</b-button>
      </div>
    </div>
  </div>
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
  import { artCall, productTypes, ratings } from '../lib'

  export default {
    name: 'Store',
    components: {AcProductPreview, AcFormContainer},
    props: ['url'],
    mixins: [Viewer, Perms, Paginated],
    data () {
      return {
        showNew: false,
        newProdModel: {
          name: '',
          category: 0,
          description: '',
          hidden: false,
          rating: 0,
          task_weight: 1,
          revisions: 1,
          max_parallel: 0,
          expected_turnaround: 3,
          price: 0,
          file: ''
        },
        newProdSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Product Name',
            model: 'name',
            price: 0,
            task_weight: 1,
            revisions: 1,
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'select',
            label: 'Category',
            model: 'category',
            featured: true,
            required: true,
            values: productTypes,
            hint: 'The medium of the product you are offering',
            selectOptions: {
              hideNoneSelectedText: true
            },
            validator: VueFormGenerator.validators.required
          }, {
            type: 'input',
            inputType: 'number',
            label: 'Price (USD)',
            model: 'price',
            step: '.01',
            min: '1.10',
            featured: true,
            required: true
          },
          {
            type: 'input',
            inputType: 'number',
            label: 'Revisions',
            model: 'revisions',
            step: '1',
            min: '0',
            hint: 'How many previews/waves of notes are offered with this piece. For instance, if you want to let the commissioner check the sketch lines before delivering a final inked piece, that would be one revision.',
            featured: true,
            required: true
          }, {
            type: 'input',
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
            type: 'input',
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
            type: 'input',
            inputType: 'number',
            label: 'Max Parallel',
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
            type: 'textArea',
            label: 'Description',
            model: 'description',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Hidden?',
            model: 'hidden',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'This product will not be visible on your storefront.'
          }, {
            type: 'select',
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
            type: 'image',
            id: 'file',
            label: 'File',
            model: 'file',
            required: true
          }]
        },
        newProdOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      populateProducts (response) {
        this.response = response
        this.growing = response.results
      },
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
    created () {
      artCall(this.url, 'GET', undefined, this.populateProducts, this.$error)
    }
  }
</script>
