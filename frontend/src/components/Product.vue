<template>
  <v-container>
    <div v-if="product">
      <v-speed-dial v-if="controls" bottom right fixed v-model="editing" elevation-10 style="z-index: 4">
        <v-btn v-if="controls"
               dark
               color="blue"
               fab
               hover
               slot="activator"
               v-model="editing"
        >
          <v-icon>lock</v-icon>
          <v-icon>lock_open</v-icon>
        </v-btn>
        <ac-action
            variant="danger" :confirm="true" :success="goToStore"
            :url="`/api/sales/v1/account/${this.username}/products/${this.product.id}/`"
            method="DELETE"
            dark small color="red" fab
        ><v-icon>delete</v-icon>
          <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this product? This cannot be undone!</div>
        </ac-action>
      </v-speed-dial>
      <v-card elevation-1>
        <v-layout row wrap>
          <v-flex xs12 md6 lg4 class="text-xs-center pr-1 pl-2 pt-1">
            <ac-asset :asset="product" thumb-name="preview" img-class="bound-image" />
          </v-flex>
          <v-flex xs12 md6 class="pt-3 pl-2">
            <h1><ac-patchfield v-model="product.name" name="name" :editmode="editing" styleclass="h1" :url="url" /> <v-icon v-if="product.hidden">visibility_off</v-icon></h1>
            <ac-patchfield v-model="product.description" name="description" :multiline="true" :editmode="editing" :url="url" />
            <p v-if="(product.tags.length === 0) && editing">
              Add some tags to describe your product. This helps your product get found in search results.
            </p>
            <ac-tag-display
                :editable="editing"
                :url="`${url}tag/`"
                :callback="setProduct"
                :tag-list="product.tags"
                :controls="controls && editing"
                v-if="product.tags.length || editing"
            />
          </v-flex>
          <v-flex md6 xs12 lg2 class="text-xs-center pt-3 pl-2">
            <div class="avatar-container">
              <ac-avatar :user="product.user" />
            </div>
            <div class="extra-details">
              <div class="full-width">
                <strong class="day-count"><ac-patchfield v-model="product.expected_turnaround" :display-value="turnaround" name="expected_turnaround" :editmode="editing" styleclass="day-count" :url="url" /></strong> days
                turnaround
              </div>
              <div class="full-width">
                <strong><ac-patchfield styleclass="revision-count" v-model="product.revisions" name="revisions" :editmode="editing" :url="url" /></strong> included revision<span v-if="product.revisions > 1">s</span>
              </div>
            </div>
            <div class="price-container">
              Starting at
              <div class="price-highlight">
                <sup class="mini-dollar">$</sup><ac-patchfield v-model="product.price" name="price" :editmode="editing" :url="url" />
              </div>
            </div>
            <div v-if="editing">
              Task weight: <ac-patchfield v-model="product.task_weight" name="task_weight" :editmode="editing" :url="url" /><br />
              Max parallel: <ac-patchfield v-model="product.max_parallel" name="max_parallel" :editmode="editing" :url="url" /><br />
              <ac-patchbutton v-if="user.username && user.rating > 0" :url="url" :classes="{'btn-sm': true, 'm-0': true}" name="sfw_mode" v-model="product.hidden" true-text="Hide Product" true-variant="success" false-text="Unhide Product" />
            </div>
          </v-flex>
        </v-layout>
      </v-card>
      <div class="mt-3"></div>
      <ac-asset-gallery ref="assetGallery" :endpoint="`${url}examples/`" :limit="5" :header="true">
        <div slot="header" class="col-12 text-xs-center mb-2">
          <v-card>
            <v-layout row wrap>
              <v-flex xs12>
                <h2>Samples</h2>
              </v-flex>
            </v-layout>
          </v-card>
        </div>
      </ac-asset-gallery>
      <div class="row-centered">
        <div class="col-12 pt-3 col-md-8 col-centered text-xs-center mb-3">
          <v-btn color="primary" size="lg" @click="showOrder = true">Order</v-btn>
        </div>
      </div>
      <v-dialog
          v-model="showOrder"
          fullscreen
          transition="dialog-bottom-transition"
          :overlay="false"
          scrollable
      >
        <v-card tile>
          <v-toolbar card dark color="primary">
            <v-btn icon @click.native="showOrder = false" dark>
              <v-icon>close</v-icon>
            </v-btn>
            <v-toolbar-title>New Order</v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn dark flat @click.prevent="$refs.newOrderForm.submit">Submit</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text>
            <form>
              <ac-form-container ref="newOrderForm" :schema="newOrderSchema" :model="newOrderModel"
                                 :options="newOrderOptions" :success="goToOrder"
                                 :url="`/api/sales/v1/account/${username}/products/${productID}/order/`"
              />
            </form>
          </v-card-text>
        </v-card>
      </v-dialog>
    </div>
    <div class="row" v-else>
      <div class="text-xs-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
  </v-container>

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
  import AcAssetGallery from './ac-asset-gallery'
  import AcTagDisplay from './ac-tag-display'

  export default {
    props: ['productID'],
    mixins: [Viewer, Perms, Editable],
    components: {
      AcTagDisplay,
      AcAssetGallery,
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
    computed: {
      turnaround () {
        return Math.ceil(this.product.expected_turnaround)
      }
    },
    data () {
      return {
        name: 'Product',
        product: null,
        url: `/api/sales/v1/account/${this.username}/products/${this.productID}/`,
        showOrder: false,
        newOrderModel: {
          details: '',
          private: false,
          characters: []
        },
        newOrderSchema: {
          fields: [{
            type: 'character-search',
            model: 'characters',
            label: 'Characters',
            featured: true,
            placeholder: 'Search characters',
            commission: true,
            styleClasses: 'field-input'
          }, {
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Private order?',
            model: 'private',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: (
              'Hides the resulting submission from public view and tells the artist you want this commission to ' +
              'be private. The artist may charge an additional fee, since they will not be able to use the piece ' +
              'in their portfolio.'
            )
          }, {
            type: 'v-text',
            label: 'Details',
            model: 'details',
            multiLine: true,
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