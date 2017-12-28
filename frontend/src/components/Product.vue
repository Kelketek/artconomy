<template>
  <div class="container product-container">
    <div v-if="product">
      <div class="row shadowed">
        <div class="col-lg-4 col-sm-12 col-md-6 text-section text-center">
          <ac-asset :asset="product" thumb-name="preview" img-class="bound-image"></ac-asset>
        </div>
        <div class="col-md-6 col-sm-12 text-section pt-3">
          <i v-if="controls && !editing" class="ml-2 fa fa-2x fa-lock clickable pull-right" @click="edit"></i>
          <i v-if="controls && editing" class="ml-2 fa fa-2x fa-unlock clickable pull-right" @click="lock"></i>
          <div v-if="controls" class="pull-right">
            <ac-action :button="false"
                       variant="danger" :confirm="true" :success="goToStore"
                       :url="`/api/sales/v1/${this.username}/products/${this.product.id}/`"
                       method="DELETE" class="fg-dark"
            ><i class="fg-light fa fa-trash-o fa-2x"></i>
              <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this product? This cannot be undone!</div>
            </ac-action>
          </div>
          <ac-patchfield v-model="product.name" name="name" :editmode="editing" styleclass="h1" :url="url"></ac-patchfield> <i v-if="product.hidden" class="fa fa-2x fa-eye-slash"></i>
          <ac-patchfield v-model="product.description" name="description" :multiline="true" :editmode="editing" :url="url"></ac-patchfield>
        </div>
        <div class="col-md-6 col-sm-12 col-lg-2 text-section text-center pt-3">
          <div class="avatar-container">
            <ac-avatar :user="product.user"></ac-avatar>
          </div>
          <div class="extra-details">
            <div class="full-width">
              <strong class="day-count"><ac-patchfield v-model="product.expected_turnaround" name="expected_turnaround" :editmode="editing" styleclass="day-count" :url="url"></ac-patchfield></strong> days
              turnaround
            </div>
            <div class="full-width">
              <strong><ac-patchfield styleclass="revision-count" v-model="product.revisions" name="revisions" :editmode="editing" :url="url"></ac-patchfield></strong> included revision<span v-if="product.revisions > 1">s</span>
            </div>
          </div>
          <div class="price-container">
            Starting at
            <div class="price-highlight">
              <sup class="mini-dollar">$</sup><ac-patchfield v-model="product.price" name="price" :editmode="editing" :url="url"></ac-patchfield>
            </div>
          </div>
          <div v-if="editing">
            Task weight: <ac-patchfield v-model="product.task_weight" name="task_weight" :editmode="editing" :url="url"></ac-patchfield><br />
            Max parallel: <ac-patchfield v-model="product.max_parallel" name="max_parallel" :editmode="editing" :url="url"></ac-patchfield><br />
            <ac-patchbutton v-if="user.username && user.rating > 0" :url="url" :classes="{'btn-sm': true, 'm-0': true}" name="sfw_mode" v-model="product.hidden" true-text="Hide Product" true-variant="success" false-text="Make Product Public"></ac-patchbutton>
          </div>
        </div>
      </div>
      <div class="row-centered" v-if="controls">
        <div class="col-sm-12 pt-3 col-md-4 col-centered text-center">
          <div v-if="showOrder">
            <form>
              <ac-form-container ref="newOrderForm" :schema="newOrderSchema" :model="newOrderModel"
                                 :options="newOrderOptions" :success="goToOrder"
                                 :url="`/api/sales/v1/${this.viewer.username}/orders/`"
              >
                <b-button @click="showOrder = false">Cancel</b-button>
                <b-button type="submit" variant="primary" @click.prevent="$refs.newOrderForm.submit">Submit</b-button>
              </ac-form-container>
            </form>
          </div>
          <b-button v-else variant="primary" size="lg" @click="showOrder=true" id="new-char-button">Order</b-button>
        </div>
      </div>
    </div>
    <div class="row" v-else>
      <div class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
  </div>
</template>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import AcAsset from '../components/ac-asset'
  import AcAction from '../components/ac-action'
  import { artCall } from '../lib'
  import AcPatchfield from './ac-patchfield'
  import AcPatchbutton from './ac-patchbutton'
  import AcFormContainer from './ac-form-container'
  import AcAvatar from './ac-avatar'

  export default {
    props: ['productID'],
    mixins: [Viewer, Perms, Editable],
    components: {
      AcAvatar,
      AcPatchfield,
      AcAsset,
      AcAction,
      AcPatchbutton,
      AcFormContainer
    },
    methods: {
      setProduct (response) {
        this.product = response
      },
      goToStore: function () {
        this.$router.history.push({name: 'Store', params: {username: this.username}})
      },
      goToOrder (response) {
        this.$router.history.push(
          {name: 'Order', params: {orderID: response.id}, query: {editing: true}}
        )
      }
    },
    data () {
      return {
        product: null,
        url: `/api/sales/v1/${this.username}/products/${this.productID}/`,
        showOrder: false,
        newOrderModel: {
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
        newOrderSchema: {
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
            type: 'image',
            id: 'file',
            label: 'File',
            model: 'file',
            required: true
          }]
        },
        newOrderOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.setProduct)
    }
  }
</script>

<style>
  .price-highlight {
    font-weight: bold;
    font-size: 2rem;
  }
  .day-count {
    font-size: 2rem;
  }
  .day-count input.patch-input {
    width: 4rem;
  }
  .revision-count input.patch-input {
    width: 2rem;
  }
</style>