<template>
  <ac-load-section :controller="product" v-if="currentRoute">
    <template v-slot:default>
      <v-layout row wrap class="ma-2">
        <v-flex xs12 hidden-md-and-up style="position: relative">
          <ac-sample-editor v-model="showChangePrimary" :large="true" :username="username" :product="product" :product-id="productId" :samples="samples" />
          <div class="edit-overlay" v-if="editing" v-ripple="{ center: true }" @click="showChangePrimary = true">
            <v-container fluid class="pa-0 edit-container">
              <v-layout column justify-content align-center d-flex class="edit-layout">
                <v-flex d-flex>
                  <v-layout row wrap align-center justify-content>
                    <v-flex text-xs-center class="edit-cta">
                      <slot name="edit-prompt">
                        <v-icon large>photo_camera</v-icon>
                        <p>Edit</p>
                      </slot>
                    </v-flex>
                  </v-layout>
                </v-flex>
              </v-layout>
            </v-container>
            <div class="backdrop"></div>
          </div>
          <v-carousel height="60vh" :cycle="false" :hide-controls="slides.length <= 1" :hide-delimiters="slides.length <= 1">
            <v-carousel-item v-if="product.x.primary_submission === null">
              <ac-asset thumb-name="thumbnail" :asset="null" :contain="true" :terse="true"></ac-asset>
            </v-carousel-item>
            <v-carousel-item v-for="sample in slides" :key="sample.id">
              <ac-gallery-preview :submission="sample"
                        thumb-name="thumbnail" :terse="true"
                        :text="false" :show-footer="false"
              />
            </v-carousel-item>
          </v-carousel>
        </v-flex>
        <v-flex md4 lg5 hidden-sm-and-down>
          <v-responsive max-height="80vh">
            <v-layout row wrap>
              <v-flex xs2 v-if="showExtra">
                <v-layout column>
                  <v-flex pa-1 v-for="sample in slides" @click.capture.stop.prevent="shown = sample" @mouseover="shown = sample"
                          :key="sample.id"
                  >
                    <ac-asset :asset="sample"
                              thumb-name="thumbnail" :terse="true"
                              :text="false"
                              :class="{submissionSelected: (shown && shown.id === sample.id)}"
                    />
                  </v-flex>
                </v-layout>
              </v-flex>
              <v-flex :class="{md10: showExtra, md12: !showExtra}">
                <ac-link :to="shownSubmissionLink">
                  <ac-asset :asset="shown"
                            thumb-name="gallery" :terse="true"
                            :editing="editing"
                            v-model="showChangePrimary"
                  >
                    <template slot="edit-prompt">
                      <v-icon large>photo_camera</v-icon>
                      <p>Add/Edit Samples</p>
                    </template>
                    <template slot="edit-menu">
                      <ac-sample-editor v-model="showChangePrimary" :large="true" :username="username" :product="product" :product-id="productId" :samples="samples" />
                    </template>
                  </ac-asset>
                </ac-link>
              </v-flex>
            </v-layout>
          </v-responsive>
        </v-flex>
        <v-flex xs12 md5 lg5 :class="{'px-2': $vuetify.breakpoint.mdAndUp}">
          <v-toolbar dense>
            <ac-avatar :username="username" :show-name="false"></ac-avatar>
            <v-toolbar-title>{{username}}</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-flex shrink d-flex v-if="controls">
              <v-layout row align-center justify-content>
                <v-flex>
                  <v-menu offset-x left>
                    <template v-slot:activator="{on}">
                      <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
                    </template>
                    <v-list dense>
                      <v-list-tile @click.stop="product.patch({hidden: !product.x.hidden})">
                        <v-list-tile-action>
                          <v-icon v-if="product.x.hidden">visibility_off</v-icon>
                          <v-icon v-else>visibility</v-icon>
                        </v-list-tile-action>
                        <v-list-tile-title>
                          <span v-if="product.x.hidden">Hidden</span>
                          <span v-else>Public</span>
                        </v-list-tile-title>
                      </v-list-tile>
                      <ac-confirmation :action="deleteProduct">
                        <template v-slot:default="confirmContext">
                          <v-list-tile v-on="confirmContext.on">
                            <v-list-tile-action class="delete-button"><v-icon>delete</v-icon></v-list-tile-action>
                            <v-list-tile-title>Delete</v-list-tile-title>
                          </v-list-tile>
                        </template>
                      </ac-confirmation>
                    </v-list>
                  </v-menu>
                </v-flex>
              </v-layout>
            </v-flex>
          </v-toolbar>
          <v-card>
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12>
                  <ac-patch-field label="Title" :patcher="product.patchers.name"
                                  v-if="controls" v-show="editing" />
                  <h1 v-show="!editing">{{product.x.name}}</h1>
                </v-flex>
                <v-flex xs12>
                  <v-layout row>
                    <v-flex shrink>
                      <v-rating :value="product.x.user.stars" dense small half-increments readonly v-if="product.x.user.stars"></v-rating>
                    </v-flex>
                    <v-flex shrink px-2 text-xs-center v-if="product.x.user.stars"><v-divider vertical/></v-flex>
                    <v-flex shrink><v-icon small>visibility</v-icon> {{product.x.hits}}</v-flex>
                    <v-spacer></v-spacer>
                    <v-flex shrink v-if="product.x.featured" v-show="!editing">
                      <v-chip small color="success"><v-avatar><v-icon>star</v-icon></v-avatar>Featured!</v-chip>
                    </v-flex>
                  </v-layout>
                  <v-divider />
                </v-flex>
                <v-flex xs12 class="pt-2">
                  <ac-rendered :value="product.x.description" v-show="!editing"/>
                  <ac-patch-field
                      field-type="ac-editor"
                      :auto-save="false"
                      :patcher="product.patchers.description"
                      v-if="controls"
                      v-show="editing"
                      label="Description"
                      hint="Tell the customer more about what you're offering."
                      :save-comparison="product.x.description"/>
                </v-flex>
                <v-flex xs12>
                  <v-divider></v-divider>
                  <ac-tag-display :patcher="product.patchers.tags"
                                  :editable="controls"
                                  :username="username"
                                  scope="Products"
                  ></ac-tag-display>
                </v-flex>
                <v-flex xs12>
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template v-slot:default>
                      <v-subheader v-if="subjectHandler.artistProfile.x.commission_info" v-show="!editing">Commission Info</v-subheader>
                      <ac-rendered :value="subjectHandler.artistProfile.x.commission_info" :truncate="500" v-show="!editing" />
                      <ac-patch-field
                              field-type="ac-editor"
                              :auto-save="false"
                              :patcher="subjectHandler.artistProfile.patchers.commission_info"
                              v-if="controls"
                              v-show="editing"
                              label="Commission Info"
                              hint="This information will be shown on ALL of your product pages. It could contain terms of service or
              other information used to set expectations with your clients."
                              :save-comparison="subjectHandler.artistProfile.x.commission_info" />
                    </template>
                  </ac-load-section>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex xs12 md3 lg2>
          <v-card :color="$vuetify.theme.darkBase.darken2">
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12 title>
                  ${{product.x.price.toFixed(2)}}
                  <v-btn v-show="editing" icon color="primary" @click="showTerms = true"><v-icon>edit</v-icon></v-btn>
                  <ac-expanded-property v-model="showTerms" :large="true">
                    <span slot="title">Edit Terms</span>
                    <v-layout row wrap>
                      <v-flex xs12 sm6>
                        <ac-patch-field :patcher="product.patchers.price" field-type="ac-price-field" :save-comparison="product.x.price"></ac-patch-field>
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-price-preview :price="product.patchers.price.model" :username="username"></ac-price-preview>
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-patch-field :patcher="product.patchers.expected_turnaround" number
                                        label="Expected Days Turnaround"
                                        hint="How many standard business days you expect this task to take (on average)."
                                        :persistent-hint="true"
                        />
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-patch-field :patcher="product.patchers.revisions" number
                                        label="Included Revisions"
                                        hint="How many revisions you're offering with this product. This does not include final
                                      delivery-- only intermediate WIP steps."
                                        :persistent-hint="true"
                        />
                      </v-flex>
                    </v-layout>
                  </ac-expanded-property>
                </v-flex>
                <v-flex>
                  <p v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </p>
                  <p>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></p>
                </v-flex>
                <v-flex xs12 text-xs-center>
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template v-slot:default>
                      <ac-escrow-label :escrow="!escrowDisabled" name="product"></ac-escrow-label>
                    </template>
                  </ac-load-section>
                </v-flex>
                <v-flex xs12>
                  <v-btn color="green" block :to="{name: 'NewOrder', params: {username, productId}}" v-if="product.x.available">
                    <v-icon left>shopping_basket</v-icon>
                    Order
                  </v-btn>
                  <v-alert v-else :value="true" type="info">This product is not currently available.</v-alert>
                </v-flex>
                <v-flex xs12>
                  <ac-share-button :title="product.x.name" :block="true" />
                </v-flex>
                <v-flex xs12 text-xs-center>
                  <v-flex v-if="escrowDisabled">
                    <p>Artconomy gives no guarantees on products ordered without Artconomy Shield, and <em><strong>ordering is
                      at your own
                      risk</strong></em>. Your artist will instruct you on how to pay them.</p>
                  </v-flex>
                  <v-flex v-else>
                    Artconomy guarantees this purchase.
                  </v-flex>
                </v-flex>
                <v-flex xs12 text-xs-center v-if="editing">
                  <v-btn color="warning" block @click="showWorkload = true">
                    <v-icon left>settings</v-icon>
                    Workload
                  </v-btn>
                  <ac-expanded-property v-model="showWorkload" :large="true">
                    <span slot="title">Edit Workload Settings</span>
                    <v-layout row wrap>
                      <v-flex xs12 sm6>
                        <h2>AWOO Workload Settings</h2>
                        <v-divider></v-divider>
                        <p>You can set these settings to help the Artconomy Workdload Organization and Overview tool manage your workload for you.</p>
                        <p><strong>If you're not sure what to do here, or would like to set these settings later, the defaults should be safe.</strong></p>
                      </v-flex>
                      <v-flex xs12 sm6>
                        <ac-patch-field :patcher="product.patchers.task_weight" number
                                        label="Slots"
                                        hint="How many slots an order of this product should take up. If this task is
                                        particularly big, you may want it to take up more than one slot."
                                        :persistent-hint="true"
                        />
                      </v-flex>
                      <v-flex xs12 sm6>
                        <v-checkbox v-model="limitAtOnce" :persistent-hint="true"
                                    label="Limit Availability"
                                    hint="If you would like to make sure you're never doing more than a few of these at a time, check this box."
                        />
                      </v-flex>
                      <v-flex xs12 sm6 v-if="limitAtOnce">
                        <ac-patch-field :persistent-hint="true"
                                        :patcher="product.patchers.max_parallel"
                                        type="number"
                                        label="Maximum at Once"
                                        min="1"
                                        hint="If you already have this many orders of this product, don't allow customers to order any more."
                        />
                      </v-flex>
                    </v-layout>
                  </ac-expanded-property>
                </v-flex>
                <v-flex xs12 v-if="isStaff" v-show="editing" text-xs-center>
                  <ac-patch-field :patcher="product.patchers.featured" field-type="v-switch" label="Featured"></ac-patch-field>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
        </v-flex>
        <v-flex xs12 class="pt-5">
          <v-toolbar color="secondary" dense><v-toolbar-title>You might also like...</v-toolbar-title></v-toolbar>
          <v-card :color="$vuetify.theme.darkBase.darken4">
            <v-card-text class="px-0" v-if="recommended">
              <ac-load-section :controller="recommended">
                <template v-slot:default>
                  <v-layout row wrap>
                    <v-flex xs6 sm4 md3 v-for="product in recommended.list" :key="product.x.id" class="pa-1">
                      <ac-product-preview :product="product.x"></ac-product-preview>
                    </v-flex>
                  </v-layout>
                </template>
              </ac-load-section>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
      <ac-editing-toggle v-if="controls"></ac-editing-toggle>
    </template>
  </ac-load-section>
  <router-view v-else></router-view>
</template>

<style lang="sass" scoped>
  .submissionSelected
    -webkit-box-shadow: 0px 0px 5px 3px rgba(255,210,149,0.62)
    box-shadow: 0px 0px 5px 3px rgba(255,210,149,0.62)
  .edit-overlay
    position: absolute
    width: 100%
    height: 100%
    z-index: 1
    .edit-container, .edit-layout
      height: 100%
    .edit-layout
      position: relative
    .backdrop
      background-color: #000000
      opacity: .40
      width: 100%
      height: 100%
      position: absolute
      top: 0
    .edit-cta
      position: relative
      z-index: 1
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller'
import Product from '@/types/Product'
import {Watch} from 'vue-property-decorator'
import AcAsset from '@/components/AcAsset.vue'
import Formatting from '@/mixins/formatting'
import Editable from '@/mixins/editable'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPricePreview from '@/components/AcPricePreview.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {Fragment} from 'vue-fragment'
import AcSampleEditor from '@/components/views/product/AcSampleEditor.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {RawLocation} from 'vue-router'
import LinkedSubmission from '@/types/LinkedSubmission'
import ProductCentric from '@/components/views/product/mixins/ProductCentric'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import {setMetaContent, textualize, updateTitle} from '@/lib'
import AcShareButton from '@/components/AcShareButton.vue'

  @Component({
    components: {
      AcShareButton,
      AcEscrowLabel,
      AcProductPreview,
      AcGalleryPreview,
      AcSampleEditor,
      AcPaginated,
      AcTagDisplay,
      AcPricePreview,
      AcExpandedProperty,
      AcRendered,
      AcPatchField,
      AcEditingToggle,
      AcConfirmation,
      AcProfileHeader,
      AcLink,
      AcAvatar,
      AcAsset,
      AcLoadSection,
      Fragment,
    },
  })
export default class ProductDetail extends mixins(ProductCentric, Formatting, Editable) {
    // Need meta tags
    public showTerms = false
    public showWorkload = false
    public showChangePrimary = false
    public shown: null|Submission = null
    public samples: ListController<LinkedSubmission> = null as unknown as ListController<LinkedSubmission>
    public recommended: ListController<Product> = null as unknown as ListController<Product>

    public get escrowDisabled() {
      if (!this.subjectHandler.artistProfile.x) {
        return true
      }
      return this.subjectHandler.artistProfile.x.escrow_disabled
    }

    public get shownSubmissionLink(): RawLocation|null {
      if (!this.shown) {
        return null
      }
      if (this.editing) {
        return null
      }
      return {name: 'Submission', params: {submissionId: this.shown.id + ''}}
    }

    @Watch('product.x')
    public updateMeta(product: Product|null) {
      if (!product) {
        return
      }
      updateTitle(`${product.name} by ${product.user.username} -- Artconomy`)
      setMetaContent('description', textualize(product.description).slice(0, 160))
    }

    @Watch('product.x.primary_submission')
    public updateShown(value: undefined|null|Submission) {
      if (value === undefined) {
        return
      }
      this.shown = value
    }

    public get currentRoute() {
      return this.$route.name === 'Product'
    }

    public get limitAtOnce() {
      return this.product.patchers.max_parallel.model !== 0
    }

    public set limitAtOnce(val: boolean) {
      const field = this.product.patchers.max_parallel
      if (val) {
        field.model = field.model || 1
      } else {
        field.model = 0
      }
    }

    public get more() {
      let diff = 0
      const product = this.product.x as Product
      if (product.primary_submission) {
        diff = 1
      }
      return (this.prunedSubmissions.length < (this.samples.list.length - diff))
    }

    public get showExtra() {
      return this.prunedSubmissions.length
    }

    public get slides() {
      const list = this.prunedSubmissions.map((x) => (x.x as LinkedSubmission).submission)
      if (this.product.x && this.product.x.primary_submission) {
        list.unshift(this.product.x.primary_submission)
      }
      return list
    }

    public get prunedSubmissions() {
      let submissions = [...this.samples.list]
      if (this.product.x && this.product.x.primary_submission) {
        const primary = this.product.x.primary_submission
        submissions = submissions.filter(
          (submission: SingleController<LinkedSubmission>) =>
            submission.x && submission.x.submission.id !== primary.id
        )
      }
      return submissions.slice(0, 4)
    }

    public deleteProduct() {
      this.product.delete().then(() => {
        this.$router.replace({name: 'Profile', params: {username: this.username}})
      })
    }

    public created() {
      this.product.get().then((product: Product) => {
        this.shown = product.primary_submission
      }).catch(this.setError)
      this.samples = this.$getList(`product__${this.productId}__samples`, {endpoint: `${this.url}samples/`})
      this.samples.firstRun()
      this.recommended = this.$getList(
        `product__${this.productId}__recommendations`, {endpoint: `${this.url}recommendations/`, pageSize: 12}
      )
      this.recommended.firstRun()
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.$listenForForm(`product${this.productId}__order`)
    }
}
</script>
