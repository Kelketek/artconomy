<template>
  <ac-load-section :controller="product" itemscope itemtype="http://schema.org/Product" v-if="currentRoute" class="pt-3">
    <template v-slot:default>
      <v-row>
        <v-col class="hidden-md-and-up" cols="12" style="position: relative" v-if="$vuetify.breakpoint.smAndDown">
          <ac-sample-editor v-model="showChangePrimary" :large="true" :username="username" :product="product" :product-id="productId" :samples="samples" />
          <div class="edit-overlay" v-if="editing" v-ripple="{ center: true }" @click="showChangePrimary = true">
            <v-container fluid class="pa-0 edit-container">
              <v-col class="edit-layout justify-content d-flex">
                <v-col class="d-flex" >
                  <v-row no-gutters class="justify-content"   align="center" >
                    <v-col class="edit-cta text-center">
                      <slot name="edit-prompt">
                        <v-icon large>photo_camera</v-icon>
                        <p>Edit</p>
                      </slot>
                    </v-col>
                  </v-row>
                </v-col>
              </v-col>
            </v-container>
            <div class="backdrop"></div>
          </div>
          <v-carousel height="60vh" :cycle="false" :show-arrows="slides.length > 1" :hide-delimiters="slides.length <= 1">
            <v-carousel-item v-if="product.x.primary_submission === null">
              <ac-asset thumb-name="thumbnail" :asset="null" :contain="true" :terse="true" />
            </v-carousel-item>
            <v-carousel-item v-for="sample in slides" :key="sample.id">
              <ac-gallery-preview :submission="sample"
                        thumb-name="thumbnail" :terse="true"
                        :text="false" :show-footer="false"
              />
            </v-carousel-item>
          </v-carousel>
        </v-col>
        <v-col v-else md="4" lg="5" >
          <v-responsive max-height="80vh">
            <v-row no-gutters  >
              <v-col cols="2" v-if="showExtra">
                <v-col>
                  <v-col class="pa-1" v-for="sample in slides" @click.capture.stop.prevent="shown = sample" @mouseover="shown = sample"
                          :key="sample.id"
                  >
                    <ac-asset :asset="sample"
                              thumb-name="thumbnail" :terse="true"
                              :text="false"
                              :class="{submissionSelected: (shown && shown.id === sample.id)}"
                    />
                  </v-col>
                </v-col>
              </v-col>
              <v-col :class="{md10: showExtra, md12: !showExtra}">
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
              </v-col>
            </v-row>
          </v-responsive>
        </v-col>
        <v-col cols="12" md="5" lg="5" :class="{'px-2': $vuetify.breakpoint.mdAndUp}">
          <v-toolbar dense color="black">
            <ac-avatar :username="username" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(subject)">{{username}}</ac-link></v-toolbar-title>
            <v-spacer />
            <v-col class="shrink d-flex" v-if="controls">
              <v-row no-gutters class="justify-content"  align="center" >
                <v-col>
                  <v-menu offset-x left :close-on-content-click="false">
                    <template v-slot:activator="{on}">
                      <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
                    </template>
                    <v-list dense>
                      <v-list-item @click.stop="editing = !editing">
                        <v-list-item-action>
                          <v-icon v-if="editing">lock</v-icon>
                          <v-icon v-else>edit</v-icon>
                        </v-list-item-action>
                        <v-list-item-title v-if="editing">Lock</v-list-item-title>
                        <v-list-item-title v-else>Edit</v-list-item-title>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-action>
                          <v-switch v-model="product.patchers.hidden.model"
                                    :hide-details="true"
                          />
                        </v-list-item-action>
                        <v-list-item-title>
                          Hidden
                        </v-list-item-title>
                      </v-list-item>
                      <ac-confirmation :action="deleteProduct">
                        <template v-slot:default="confirmContext">
                          <v-list-item v-on="confirmContext.on">
                            <v-list-item-action class="delete-button"><v-icon>delete</v-icon></v-list-item-action>
                            <v-list-item-title>Delete</v-list-item-title>
                          </v-list-item>
                        </template>
                      </ac-confirmation>
                    </v-list>
                  </v-menu>
                </v-col>
              </v-row>
            </v-col>
          </v-toolbar>
          <v-card>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <ac-patch-field label="Title" :patcher="product.patchers.name"
                                  v-if="controls" v-show="editing" />
                  <h1 v-show="!editing" itemprop="name">{{product.x.name}}</h1>
                </v-col>
                <v-col cols="12">
                  <v-row dense>
                    <v-col class="shrink">
                      <router-link :to="{name: 'Ratings', params: {username}}" itemprop="aggregateRating"
                                   itemscope itemtype="http://schema.org/AggregateRating" v-if="product.x.user.stars">
                        <span itemprop="ratingValue" :content="product.x.user.stars"></span>
                        <span itemprop="ratingCount" :content="product.x.user.rating_count"></span>
                        <v-rating :value="product.x.user.stars" dense small half-increments readonly v-if="product.x.user.stars" />
                      </router-link>
                    </v-col>
                    <v-col class="shrink text-center" v-if="product.x.user.stars"><v-divider vertical/></v-col>
                    <v-col class="shrink"><v-chip small><v-icon left>visibility</v-icon> {{product.x.hits}}</v-chip></v-col>
                    <v-col class="text-right" v-if="product.x.featured">
                      <v-chip small color="success"><v-avatar><v-icon>star</v-icon></v-avatar>Featured!</v-chip>
                    </v-col>
                  </v-row>
                  <v-divider />
                </v-col>
                <v-col cols="12" class="pt-2">
                  <ac-rendered :value="product.x.description" v-show="!editing" itemprop="description" />
                  <ac-patch-field
                      field-type="ac-editor"
                      :auto-save="false"
                      :patcher="product.patchers.description"
                      v-if="controls"
                      v-show="editing"
                      label="Description"
                      hint="Tell the customer more about what you're offering."
                      :save-comparison="product.x.description"/>
                </v-col>
                <v-col cols="12" class="my-2"><v-divider /></v-col>
                <v-col cols="12">
                  <ac-tag-display :patcher="product.patchers.tags"
                                  :editable="controls"
                                  :username="username"
                                  scope="Products"
                  />
                </v-col>
                <v-col cols="12">
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template v-slot:default>
                      <v-row no-gutters>
                        <v-col cols="12" class="my-2">
                          <strong>Maximum Content Rating:</strong>
                          <v-btn class="mx-2 rating-button" x-small :color="ratingColor[product.x.max_rating]" @click="showRating" :ripple="editing">
                            <v-icon left v-if="editing">edit</v-icon>
                            {{ratingsShort[product.x.max_rating]}}
                          </v-btn>
                          <ac-expanded-property v-model="ratingDialog">
                            <ac-patch-field field-type="ac-rating-field" :patcher="product.patchers.max_rating" />
                          </ac-expanded-property>
                        </v-col>
                        <v-col cols="12">
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
                        </v-col>
                      </v-row>
                    </template>
                  </ac-load-section>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="3" lg="2">
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text>
              <v-row dense>
                <v-col class="title" cols="12">
                  <span v-if="product.patchers.name_your_price.model">Name Your Price!</span>
                  <fragment v-else>
                    <span itemprop="offers" itemscope itemtype="http://schema.org/Offer" v-if="forceShield && !product.x.escrow_enabled && product.x.escrow_upgradable">
                      <span itemprop="priceCurrency" content="USD">$</span><span itemprop="price" :content="product.x.shield_price.toFixed(2)">{{product.x.shield_price.toFixed(2)}}</span>
                    </span>
                    <span itemprop="offers" itemscope itemtype="http://schema.org/Offer" v-else>
                      <span itemprop="priceCurrency" content="USD">$</span><span itemprop="price" :content="product.x.starting_price.toFixed(2)">{{product.x.starting_price.toFixed(2)}}</span>
                    </span>
                  </fragment>
                  <v-btn v-show="editing" icon color="primary" @click="showTerms = true"><v-icon>edit</v-icon></v-btn>
                  <ac-expanded-property v-model="showTerms" :large="true">
                    <span slot="title">Edit Terms</span>
                    <v-row>
                      <v-col cols="12" md="6" lg="4">
                        <v-row>
                          <v-col cols="12" sm="6" lg="12">
                            <ac-patch-field :patcher="product.patchers.base_price" :label="basePriceLabel"
                                            field-type="ac-price-field"
                                            :hint="priceHint"
                            />
                          </v-col>
                          <v-col cols="12" sm="6">
                            <ac-patch-field
                                :patcher="product.patchers.cascade_fees" field-type="v-switch" label="Absorb fees" :persistent-hint="true"
                                hint="If turned on, the price you set is the price your commissioner will see, and you
                          will pay all fees from that price. If turned off, the price you set is the amount you
                          take home, and the total the customer pays includes the fees."
                                :true-value="true"
                                :false-value="false"
                            />
                          </v-col>
                          <v-col cols="12" sm="6">
                            <ac-patch-field
                                :patcher="product.patchers.name_your_price" field-type="v-switch" label="Name Your Price" :persistent-hint="true"
                                hint="If turned on, the base price is treated as a minimum price to cover costs,
                                     and the client is prompted to put in their own price. This is useful for 'Pay
                                     What You Want' commissions. You should note whatever impact the price has on the
                                     commission in the product details in order to avoid any dispute issues."
                                :true-value="true"
                                :false-value="false"
                            />
                          </v-col>
                          <v-col cols="12" sm="6" v-if="subject.paypal_configured">
                            <ac-patch-field
                              :patcher="product.patchers.paypal"
                              field-type="v-switch"
                              label="PayPal Invoicing"
                              :persistent-hint="true"
                              hint="If the order is marked unshielded, generate a PayPal invoice upon acceptance."
                              :true-value="true"
                              :false-value="false"
                            />
                          </v-col>
                          <v-col cols="12" sm="6" v-if="escrow">
                            <ac-patch-field
                                :patcher="product.patchers.escrow_enabled"
                                field-type="v-switch"
                                label="Shield enabled"
                                :persistent-hint="true"
                                hint="Enable shield protection for this product."
                                :true-value="true"
                                :false-value="false"
                            />
                          </v-col>
                          <v-col cols="12" sm="6" v-if="escrow">
                            <ac-patch-field
                                :patcher="product.patchers.escrow_upgradable"
                                field-type="v-switch"
                                label="Allow Shield Upgrade"
                                :persistent-hint="true"
                                :disabled="product.patchers.escrow_enabled.model"
                                :false-value="false"
                                :true-value="true"
                                hint="Allow user to upgrade to shield at their option, rather than requiring it. When upgrading, fee absorption is always off."
                            />
                          </v-col>
                        </v-row>
                      </v-col>
                      <v-col cols="12" md="6" lg="8">
                        <ac-price-comparison
                            :username="username" :line-item-set-maps="lineItemSetMaps"
                        />
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :patcher="product.patchers.expected_turnaround" number
                                        label="Expected Days Turnaround"
                                        hint="How many standard business days you expect this task to take (on average)."
                                        :persistent-hint="true"
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :patcher="product.patchers.revisions" number
                                        label="Included Revisions"
                                        hint="How many revisions you're offering with this product. This does not include final
                                      delivery-- only intermediate WIP steps."
                                        :persistent-hint="true"
                        />
                      </v-col>
                    </v-row>
                  </ac-expanded-property>
                </v-col>
                <v-col>
                  <p v-if="forceShield && product.x.escrow_upgradable && !product.x.escrow_enabled">
                    <strong>${{product.x.starting_price.toFixed(2)}}</strong> without Artconomy Shield
                  </p>
                  <p v-else-if="product.x.escrow_upgradable && !product.x.escrow_enabled">
                    <strong>${{product.x.shield_price.toFixed(2)}}</strong> with Artconomy Shield
                  </p>
                  <p v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </p>
                  <p>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></p>
                </v-col>
                <v-col class="text-center" cols="12" >
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template v-slot:default>
                      <ac-escrow-label :escrow="product.x.escrow_enabled" :upgrade-available="product.x.escrow_upgradable" name="product" />
                    </template>
                  </ac-load-section>
                </v-col>
                <v-col cols="12">
                  <template v-if="product.x.available || isStaff || isCurrent">
                    <div class="text-center" v-if="inventory.x && inventory.x.count">
                      <p>
                        <strong>
                          {{inventory.x.count}} still available. Order now to get yours!
                        </strong>
                      </p>
                    </div>
                    <v-alert v-if="product.x.wait_list" :value="true" type="info">This product is waitlisted.</v-alert>
                    <v-btn color="green" block :to="orderLink" v-if="!product.x.table_product">
                      <v-icon left>shopping_basket</v-icon>
                      <span v-if="isCurrent">Create Invoice</span>
                      <span v-else>Order</span>
                    </v-btn>
                    <v-alert type="info" v-else>Visit our table to order!</v-alert>
                  </template>
                  <v-alert v-if="!product.x.available" :class="{'mt-2': isCurrent || isStaff}" :value="true" type="info">This product is not currently available.</v-alert>
                </v-col>
                <v-col cols="12">
                  <ac-share-button :title="product.x.name" :block="true" :media-url="shareMediaUrl" :clean="shareMediaClean" />
                </v-col>
                <v-col class="text-center" cols="12" >
                  <v-col v-if="!product.x.escrow_enabled">
                    <p>Artconomy gives no guarantees on products ordered without Artconomy Shield, and <em><strong>ordering without Shield is
                      at your own
                      risk</strong></em>. Your artist will instruct you on how to pay them.</p>
                  </v-col>
                  <v-col v-else>
                    Artconomy guarantees this purchase.
                  </v-col>
                </v-col>
                <v-col class="text-center" cols="12" v-if="editing">
                  <v-btn color="warning" block @click="showWorkload = true">
                    <v-icon left>settings</v-icon>
                    Workload
                  </v-btn>
                  <ac-expanded-property v-model="showWorkload" :large="true">
                    <span slot="title">Edit Workload Settings</span>
                    <v-row no-gutters  >
                      <v-col cols="12" class="text-center">
                        <h2>AWOO Workload Settings</h2>
                        <v-divider />
                        <p>You can set these settings to help the Artconomy Workdload Organization and Overview tool manage your workload for you.</p>
                        <p><strong>If you're not sure what to do here, or would like to set these settings later, the defaults should be safe.</strong></p>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-checkbox v-model="limitAtOnce" :persistent-hint="true"
                                    label="Limit Availability"
                                    :disabled="product.patchers.wait_list.model"
                                    hint="If you would like to make sure you're never doing more than a few of these at a time, check this box."
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :persistent-hint="true"
                                        :patcher="product.patchers.max_parallel"
                                        label="Maximum at Once"
                                        min="1"
                                        v-if="limitAtOnce"
                                        :disabled="product.patchers.wait_list.model"
                                        hint="If you already have this many orders of this product, don't allow customers to order any more."
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :patcher="product.patchers.wait_list"
                                        label="Wait List Product"
                                        field-type="ac-checkbox"
                                        :disabled="!(product.patchers.wait_list.model || subject.landscape)"
                                        hint="Marks this product as a waitlist product. Orders will be put in your
                                        waitlist queue which is separate from your normal order queue. You should specify
                                        your waitlist policy in the product description or in your commission info.
                                        This setting takes precedence over all other workload settings."
                                        :persistent-hint="true"
                        />
                        <div v-if="!subject.landscape">
                          This feature only available to <router-link :to="{name: 'Upgrade'}">Landscape</router-link> subscribers.
                        </div>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :patcher="product.patchers.task_weight" number
                                        label="Workload Points"
                                        :disabled="product.patchers.wait_list.model"
                                        hint="How many slots an order of this product should take up. If this task is
                                        particularly big, you may want it to take up more than one slot."
                                        :persistent-hint="true"
                        />
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="12" sm="6">
                        <ac-patch-field :patcher="product.patchers.track_inventory" :persistent-hint="true"
                                    v-if="isStaff || landscape || product.patchers.inventory"
                                    field-type="ac-checkbox"
                                    label="Inventory"
                                    :disabled="product.patchers.wait_list.model"
                                    hint="Check if you only want to sell this product a limited number of times total."
                        />
                      </v-col>
                      <v-col cols="12" sm="6" v-if="product.x.track_inventory">
                        <ac-load-section :controller="inventory">
                          <template v-slot:default>
                            <ac-patch-field :persistent-hint="true"
                                            :patcher="inventory.patchers.count"
                                            type="number"
                                            min="0"
                                            :disabled="product.patchers.wait_list.model"
                                            hint="Number of times left you'll allow this product to be ordered."
                            />
                          </template>
                        </ac-load-section>
                      </v-col>
                    </v-row>
                  </ac-expanded-property>
                </v-col>
                <v-col class="text-center" cols="12" v-if="isStaff" v-show="editing" >
                  <ac-patch-field :patcher="product.patchers.featured" field-type="v-switch" label="Featured" />
                </v-col>
                <v-col class="text-center" cols="12" v-if="isStaff" v-show="editing" >
                  <ac-patch-field :patcher="product.patchers.catalog_enabled" field-type="v-switch" label="Catalog Enabled" />
                </v-col>
                <v-col class="text-center" cols="12" v-if="isStaff" v-show="editing" >
                  <ac-patch-field :patcher="product.patchers.table_product" field-type="v-switch" label="Table Product" />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" class="pt-5">
          <v-toolbar color="secondary" dense><v-toolbar-title>You might also like...</v-toolbar-title></v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-card-text class="px-0" v-if="recommended">
              <ac-load-section :controller="recommended">
                <template v-slot:default>
                  <v-row no-gutters  >
                    <v-col cols="6" sm="4" md="3" v-for="product in recommended.list" :key="product.x.id" class="pa-1">
                      <ac-product-preview :product="product.x" />
                    </v-col>
                  </v-row>
                </template>
              </ac-load-section>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <ac-editing-toggle v-if="controls" />
    </template>
  </ac-load-section>
  <router-view v-else />
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
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {Fragment} from 'vue-frag'
import AcSampleEditor from '@/components/views/product/AcSampleEditor.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {RawLocation, Location} from 'vue-router'
import LinkedSubmission from '@/types/LinkedSubmission'
import ProductCentric from '@/components/views/product/mixins/ProductCentric'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import {RATING_COLOR, RATINGS_SHORT, setMetaContent, textualize, updateTitle} from '@/lib/lib'
import AcShareButton from '@/components/AcShareButton.vue'
import Pricing from '@/types/Pricing'
import Inventory from '@/types/Inventory'
import Sharable from '@/mixins/sharable'
import {deliverableLines} from '@/lib/lineItemFunctions'
import {LineItemSetMap} from '@/types/LineItemSetMap'
import AcPriceComparison from '@/components/price_preview/AcPriceComparison.vue'

@Component({
  components: {
    AcPriceComparison,
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
export default class ProductDetail extends mixins(ProductCentric, Formatting, Editable, Sharable) {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
    public inventory: SingleController<Inventory> = null as unknown as SingleController<Inventory>
    public showTerms = false
    public showWorkload = false
    public showChangePrimary = false
    public ratingDialog = false
    public shown: null|Submission = null
    public samples: ListController<LinkedSubmission> = null as unknown as ListController<LinkedSubmission>
    public recommended: ListController<Product> = null as unknown as ListController<Product>
    public ratingsShort = RATINGS_SHORT
    public ratingColor = RATING_COLOR

    public get shownSubmissionLink(): RawLocation|null {
      if (!this.shown) {
        return null
      }
      if (this.editing) {
        return null
      }
      return {name: 'Submission', params: {submissionId: this.shown.id + ''}}
    }

    public get forceShield() {
      return !!({...this.$route.query}.forceShield)
    }

    public get orderLink(): Location {
      // eslint-disable-next-line camelcase
      if (this.isCurrent && this.product.x?.over_order_limit) {
        return {name: 'Upgrade', params: {username: this.username}}
      }
      const path: Location = {
        name: 'NewOrder',
        params: {username: this.username, productId: `${this.productId}`, stepId: '1'},
      }
      path.query = {...this.$route.query}
      if (this.isCurrent) {
        path.params!.invoiceMode = 'invoice'
      }
      return path
    }

    @Watch('product.x', {deep: true})
    public updateMeta(product: Product|null, oldProduct: Product|null) {
      if (!product) {
        return
      }
      if (product && !oldProduct) {
        this.shown = product.primary_submission
      }
      updateTitle(`${product.name} by ${product.user.username} -- Artconomy`)
      let prefix: string
      if (product.starting_price) {
        prefix = `[Starts at $${product.starting_price.toFixed(2)}] - `
      } else {
        prefix = '[Starts at FREE] - '
      }
      const description = textualize(product.description).slice(0, 160 - prefix.length)
      setMetaContent('description', prefix + description)
    }

    public showRating() {
      if (this.editing) {
        this.ratingDialog = true
      }
    }

    @Watch('product.x.track_inventory')
    public getInventory(toggle: boolean, oldVal: boolean|undefined) {
      if (!toggle) {
        return
      }
      this.inventory.ready = false
      this.inventory.setX(null)
      this.inventory.get()
    }

    @Watch('showWorkload')
    public updateAvailability(newVal: boolean, oldVal: boolean) {
      if (oldVal && !newVal) {
        this.product.refresh()
      }
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

    public get lineItemSetMaps(): LineItemSetMap[] {
      const sets = []
      const product = this.product
      if (!product.x) {
        return []
      }
      const escrowLinesController = this.$getList(`product${product.x.id}LinesEscrow`, {
        endpoint: '#',
        paginated: false,
      })
      const nonEscrowLinesController = this.$getList(`product${product.x.id}LinesNonEscrow`, {
        endpoint: '#',
        paginated: false,
      })
      const preferredLinesController = this.$getList(`product${product.x.id}PreferredPlanItems`, {
        endpoint: '#',
        paginated: false,
      })
      const pricing = this.pricing.x
      const basePrice = product.x.base_price
      // eslint-disable-next-line camelcase
      const planName = this.subject?.service_plan
      const international = !!this.subject?.international
      const cascade = product.x.cascade_fees
      const tableProduct = product.x.table_product
      let appendPreferred = false
      if (this.escrow && (product.x.escrow_enabled || product.x.escrow_upgradable)) {
        const options = {
          basePrice,
          cascade: cascade && (product.x.escrow_enabled),
          international,
          pricing,
          escrowEnabled: true,
          tableProduct,
          extraLines: [],
        }
        const escrowLines = deliverableLines({
          ...options,
          planName,
        })
        escrowLinesController.makeReady(escrowLines)
        sets.push({name: 'Shielded', lineItems: escrowLinesController, offer: false})
        if (pricing && (planName !== pricing.preferred_plan)) {
          preferredLinesController.makeReady(deliverableLines({
            ...options,
            planName: pricing.preferred_plan,
          }))
          appendPreferred = true
        }
      }
      if (!this.escrow || !product.x.escrow_enabled) {
        const nonEscrowLines = deliverableLines({
          basePrice,
          cascade,
          international,
          planName,
          pricing,
          escrowEnabled: false,
          tableProduct,
          extraLines: [],
        })
        nonEscrowLinesController.makeReady(nonEscrowLines)
        sets.push({name: 'Unshielded', lineItems: nonEscrowLinesController, offer: false})
      }
      if (appendPreferred) {
        // eslint-disable-next-line camelcase
        sets.push({name: pricing?.preferred_plan + '', lineItems: preferredLinesController, offer: true})
      }
      return sets
    }

    public get shareMedia() {
      const product = this.product.x as Product
      /* istanbul ignore if */
      if (!product) {
        return null
      }
      /* istanbul ignore if */
      if (!product.primary_submission) {
        return null
      }
      return product.primary_submission
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

    public get basePriceLabel() {
      if (this.product.patchers.cascade_fees.model) {
        return 'List Price'
      } else {
        return 'Take home amount'
      }
    }

    public get escrow() {
      const profile = this.subjectHandler.artistProfile.x
      return !!(profile && profile.escrow_enabled)
    }

    public get priceHint() {
      if (this.escrow) {
        return `Enter the listing price you want to present to the user. We will calculate what
                  their fees will be for you. Adjust this number until you're happy with your cut and
                  the total price. You will be able to adjust this
                  price per-order if the client has special requests.`
      }
      return `Enter the listing price you want to present to the user. You will be able to adjust this
                price per-order if the client has special requests.`
    }

    public get slides() {
      const list = this.prunedSubmissions.map((x) => (x.x as LinkedSubmission).submission)
      if (this.product.x && this.product.x.primary_submission) {
        list.unshift(this.product.x.primary_submission)
      }
      return list
    }

    @Watch('maxSampleRating')
    public triggerAgeCheck(value: number) {
      this.ageCheck({value})
    }

    public get maxSampleRating() {
      if (!this.samples) {
        return 0
      }
      const list = this.samples.list
      const ratings = list.map((x) => {
        const linkedSubmission = x.x as LinkedSubmission
        return linkedSubmission.submission.rating
      })
      if (this.product.x && this.product.x.primary_submission) {
        ratings.push(this.product.x.primary_submission.rating)
      }
      if (!ratings.length) {
        return 0
      }
      return Math.max(...ratings)
    }

    public get prunedSubmissions() {
      let submissions = [...this.samples.list]
      if (this.product.x && this.product.x.primary_submission) {
        const primary = this.product.x.primary_submission
        submissions = submissions.filter(
          (submission: SingleController<LinkedSubmission>) =>
            submission.x && submission.x.submission.id !== primary.id,
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
      this.product.get()
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
      this.pricing.get()
      this.inventory = this.$getSingle(
        `product__${this.productId}__inventory`, {endpoint: `${this.url}inventory/`},
      )
      this.pricing.get()
      this.samples = this.$getList(`product__${this.productId}__samples`, {endpoint: `${this.url}samples/`})
      this.samples.firstRun().catch(this.statusOk(404))
      this.recommended = this.$getList(
        `product__${this.productId}__recommendations`, {endpoint: `${this.url}recommendations/`, params: {size: 12}},
      )
      this.recommended.firstRun().catch(this.statusOk(404))
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.$listenForForm(`product${this.productId}__order`)
    }
}
</script>
