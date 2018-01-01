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
        <div class="col-sm-12 pt-3 col-md-8 col-centered text-center">
          <div v-if="showOrder">
            <form>
              <ac-form-container ref="newOrderForm" :schema="newOrderSchema" :model="newOrderModel"
                                 :options="newOrderOptions" :success="goToOrder"
                                 :url="`/api/sales/v1/${username}/products/${productID}/order/`"
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
          {name: 'Order', params: {username: response.buyer.username, orderID: response.id}, query: {editing: true}}
        )
      }
    },
    data () {
      return {
        name: 'Product',
        product: null,
        url: `/api/sales/v1/${this.username}/products/${this.productID}/`,
        showOrder: false,
        newOrderModel: {
          details: '',
          characters: []
        },
        newOrderSchema: {
          fields: [{
            type: 'character-search',
            model: 'characters',
            label: 'Characters',
            featured: true,
            placeholder: 'Search characters',
            styleClasses: 'field-input'
          }, {
            type: 'textArea',
            label: 'Details',
            model: 'details',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string,
            hint: (
              'Describe, in as much detail as possible, what you would like the artist to create. ' +
              'Add links to reference images as needed. Any characters you have selected will automatically be ' +
              'shared with the artist, and any submissions that exist for these characters which have not explicitly ' +
              'been marked as private will be visible to them for reference.'
            )
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