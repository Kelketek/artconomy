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
               large
               v-model="editing"
        >
          <v-icon v-if="editing">lock</v-icon>
          <v-icon v-else>edit</v-icon>
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
            <div v-if="product.featured && !(editing && viewer.is_staff)">
              <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'featured-products'}}">
                <p><v-icon>star</v-icon>Featured Product!</p>
              </router-link>
            </div>
            <div v-else-if="editing && viewer.is_staff">
              <ac-action :url="`${this.url}feature/`" :success="setProduct">
                <span v-if="product.featured"><v-icon>star_outline</v-icon>&nbsp;Stop Featuring</span>
                <span v-else><v-icon>star</v-icon>&nbsp;Feature</span>
              </ac-action>
            </div>
          </v-flex>
          <v-flex xs12 md5 class="pt-3 pl-2">
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
            <ac-share-button :title="`${product.name} - by ${product.user.username}`" :target-rating="product.rating" v-if="!product.hidden" />
          </v-flex>
          <v-flex md6 xs12 lg3 class="text-xs-center pt-3 pl-2">
            <v-layout row wrap>
              <v-flex xs12 class="avatar-container">
                <ac-avatar :user="product.user" />
              </v-flex>
              <v-flex xs6>
                <strong>Days turnaround: </strong>
              </v-flex>
              <v-flex xs6>
                {{turnaround}}
              </v-flex>
              <v-flex xs6>
                <strong>Included revision<span v-if="product.revisions > 1">s</span>:</strong>
              </v-flex>
              <v-flex xs6>
                {{product.revisions}}
              </v-flex>
              <v-flex xs6>
                <strong>Starting at:</strong>
              </v-flex>
              <v-flex xs6>
                <span>$</span>{{product.price}}
              </v-flex>
              <v-flex xs6 v-if="editing">
                <strong>Task weight:</strong>
              </v-flex>
              <v-flex xs6 v-if="editing">
                {{product.task_weight}}
              </v-flex>
              <v-flex xs6 v-if="editing">
                <strong>Max at once:</strong>
              </v-flex>
              <v-flex xs6 v-if="editing">
                {{product.max_parallel}}
              </v-flex>
              <v-flex xs12 v-if="editing">
                <v-btn @click="showProductUpdate = true">Edit Attributes</v-btn>
              </v-flex>
              <v-flex xs12 v-if="editing">
                <v-btn @click="showImageUpdate = true">Update Images</v-btn>
              </v-flex>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-card>
      <v-card class="mt-3">
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs3 sm1 v-if="product.user.escrow_disabled">
              <v-icon large class="yellow--text">warning</v-icon>
            </v-flex>
            <v-flex xs3 sm1 v-else>
              <v-icon large class="green--text">fa-shield</v-icon>
            </v-flex>
            <v-flex xs9 sm11 text-xs-center v-if="product.user.escrow_disabled">
              <p>
                This product is not protected by
                <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                  Artconomy Shield.</router-link>
                Artconomy gives no guarantees on products ordered without Artconomy Shield, and <em><strong>ordering is at your own
                risk</strong></em>. Your artist will instruct you on how to pay them.
              </p>
            </v-flex>
            <v-flex xs9 sm11 text-xs-center v-else>
              <p>
                This product is protected by
                  <router-link :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
                    Artconomy Shield,</router-link> our escrow and dispute resolution service.
              </p>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
      <ac-form-dialog
          v-model="showImageUpdate"
          :title="`Update images for ${product.name}`"
          submit-text="Save"
          :model="imageModel"
          :options="newOrderOptions"
          :schema="imageUpdateSchema"
          method="PATCH"
          :url="url"
          :success="setProduct"
      >
      </ac-form-dialog>
      <ac-form-dialog
          v-model="showProductUpdate"
          :title="`Update attributes for ${product.name}`"
          submit-text="Save"
          :model="productModel"
          :options="newOrderOptions"
          :schema="productUpdateSchema"
          method="PATCH"
          :url="url"
          :success="setProduct"
      >
      </ac-form-dialog>
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
      <v-card>
        <v-card-text>
          <v-layout row wrap v-if="product.user.commission_info">
            <v-flex xs12 v-html="md.render(product.user.commission_info)" class="pl-2 pr-2"></v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
      <div class="row-centered">
        <div class="col-12 pt-3 col-md-8 col-centered text-xs-center mb-3">
          <v-flex v-if="isCurrent">
            <p>
              Customers may view your product if it is not hidden. If you need to allow a customer to
              order even if your queue is full, add an order token below.
            </p>
            <p>
              This product is currently
              <span v-if="product.available">available.</span>
              <span v-else>unavailable.</span>
            </p>
          </v-flex>
          <p v-else-if="!product.available && !newOrderModel.order_token">This product is not available at this time.</p>
          <v-btn color="primary" size="lg" @click="showOrder = true" v-else-if="viewer.username">Order</v-btn>
          <v-btn color="primary" size="lg" :to="{name: 'Login'}" v-else>Login or Register to Order this Product!</v-btn>
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
    <v-layout row wrapped v-else>
      <v-flex class="text-xs-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
    </v-layout>
    <ac-tokens-list :endpoint="`${url}tokens/`" v-if="isCurrent" :show-loading="product" />
  </v-container>

</template>

<script>
  import VueFormGenerator from 'vue-form-generator'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import AcAsset from '../components/ac-asset'
  import AcAction from '../components/ac-action'
  import {artCall, md, ratings, setMetaContent, textualize} from '../lib'
  import AcPatchfield from './ac-patchfield'
  import AcPatchbutton from './ac-patchbutton'
  import AcFormContainer from './ac-form-container'
  import AcAvatar from './ac-avatar'
  import AcAssetGallery from './ac-asset-gallery'
  import AcTagDisplay from './ac-tag-display'
  import AcFormDialog from './ac-form-dialog'
  import AcTokensList from './ac-tokens-list'
  import AcShareButton from './ac-share-button'

  export default {
    props: ['productID'],
    mixins: [Viewer, Perms, Editable],
    components: {
      AcShareButton,
      AcTokensList,
      AcFormDialog,
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
        this.product = {...response}
        this.productModel = {
          price: response.price,
          revisions: response.revisions,
          expected_turnaround: response.expected_turnaround,
          task_weight: response.task_weight,
          max_parallel: response.max_parallel,
          hidden: response.hidden
        }
        this.imageModel.rating = response.rating + ''
        this.showImageUpdate = false
        this.showProductUpdate = false
        document.title = `${this.product.name} by ${this.product.user.username} -- Artconomy`
        setMetaContent('description', textualize(this.product.description).slice(0, 160))
      },
      goToStore: function () {
        this.$router.history.push({name: 'Store', params: {username: this.username}})
      },
      goToOrder (response) {
        this.$router.history.push(
          {name: 'Order', params: {username: response.buyer.username, orderID: response.id}, query: {editing: true}}
        )
      },
      refreshProduct () {
        artCall(this.url, 'GET', this.$route.query, this.setProduct, this.$error)
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
        showImageUpdate: false,
        md: md,
        productModel: null,
        showProductUpdate: false,
        newOrderModel: {
          details: '',
          private: false,
          characters: [],
          order_token: this.$route.query.order_token || ''
        },
        imageModel: {
          rating: null,
          file: [],
          preview: []
        },
        imageUpdateSchema: {
          fields: [
            {
              type: 'v-select',
              label: 'Rating',
              model: 'rating',
              featured: true,
              required: true,
              values: ratings,
              hint: 'The content rating of your preview image (even if individual commissions may vary)',
              selectOptions: {
                hideNoneSelectedText: true
              }
            },
            {
              type: 'v-file-upload',
              id: 'file',
              label: 'Replace File',
              model: 'file',
              required: false
            },
            {
              type: 'v-file-upload',
              id: 'preview',
              label: 'Replace Preview Image/Thumbnail',
              model: 'preview',
              hint: 'Should be a square image. We recommend a size not smaller than 300x300 pixels.',
              required: false
            }]
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
            label: 'Order Token',
            model: 'order_token',
            placeholder: '',
            featured: true,
            hint: "This may have been given to you by the artist. If you don't have one, leave this blank."
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
        },
        productUpdateSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            label: 'Price (USD)',
            model: 'price',
            step: '.01',
            min: '1.10',
            featured: true,
            required: true
          }, {
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
            type: 'v-checkbox',
            styleClasses: ['vue-checkbox'],
            label: 'Hidden?',
            model: 'hidden',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'If checked, this product will not be visible on your storefront.'
          }]
        }
      }
    },
    created () {
      this.refreshProduct()
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