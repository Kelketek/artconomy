<template>
  <ac-load-section :controller="product">
    <template v-slot:default>
      <v-row @click="() => clickCounter += 1">
        <v-col cols="12" md="8" offset-lg="1" >
          <ac-form @submit.prevent="submitAction">
            <ac-form-container
                :errors="orderForm.errors"
                :sending="orderForm.sending"
            >
              <template slot="top-buttons" />
              <v-card>
                <v-card-title>
                  <span class="title">New Commission Order</span>
                </v-card-title>
                <v-toolbar v-if="isRegistered" dense color="black">
                  <ac-avatar :user="viewer" :show-name="false" />
                  <v-toolbar-title class="ml-1">{{viewerName}}</v-toolbar-title>
                </v-toolbar>
                <v-stepper v-model="orderForm.step" class="submission-stepper" non-linear>
                  <v-stepper-header>
                    <v-stepper-step editable :complete="orderForm.steps[1].complete" :step="1" :rules="orderForm.steps[1].rules">Basics</v-stepper-step>
                    <v-divider />
                    <v-stepper-step editable :step="2" :rules="orderForm.steps[2].rules" :complete="orderForm.steps[1].complete">Details</v-stepper-step>
                    <v-divider />
                    <v-stepper-step editable :step="3" :rules="orderForm.steps[3].rules">Notices and Agreements</v-stepper-step>
                  </v-stepper-header>
                  <v-stepper-items>
                    <v-stepper-content :step="1">
                      <v-row>
                        <v-col cols="12" sm="6" v-if="invoicing || !isRegistered || product.x.table_product">
                          <v-subheader v-if="!isRegistered">Checkout as Guest</v-subheader>
                          <v-subheader v-if="invoicing">Enter customer's username or email</v-subheader>
                          <v-subheader v-else-if="product.x.table_product">Enter Commissioner's Email</v-subheader>
                          <ac-bound-field
                                  label="Customer username/email"
                                  :field="orderForm.fields.email"
                                  item-value="username"
                                  :multiple="false"
                                  :allow-raw="true"
                                  v-if="invoicing"
                                  hint="Enter the username or the email address of the customer this commission is for.
                This can be left blank if you only want to use this order for tracking purposes."
                          />
                          <ac-bound-field label="Email" v-else :field="orderForm.fields.email" />
                        </v-col>
                        <v-col cols="12" sm="6" class="text-center" v-if="!isRegistered">
                          <p>Or, if you have an account,</p>
                          <v-btn :to="{name: 'Login', params: {tabName: 'login'}, query: {next: $route.fullPath}}" color="primary">Log in here!</v-btn>
                        </v-col>
                      </v-row>
                      <v-row v-if="product.x.max_rating > 0">
                        <v-col cols="12">
                          <ac-bound-field
                              label="Content Rating of Piece"
                              field-type="ac-rating-field" :field="orderForm.fields.rating"
                              :persistent-hint="true"
                              :max="product.x.max_rating"
                              :hint="ratingHint"
                          />
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" v-if="isRegistered && !product.x.table_product">
                          <ac-bound-field
                              field-type="ac-character-select" :field="orderForm.fields.characters" label="Characters"
                              hint="Start typing a character's name to search. If you've set up characters on Artconomy, you can
                  attach them to this order for easy referencing by the artist! If you haven't added any characters, or
                  no characters are in this piece, you may leave this blank."
                              v-if="showCharacters"
                              :init-items="initCharacters"
                          />
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" sm="6">
                          <ac-bound-field
                              field-type="ac-checkbox" :field="orderForm.fields.private" label="Private Order" :persistent-hint="true"
                              :hint="privateHint"
                          />
                        </v-col>
                        <v-col cols="12" sm="6" v-if="product.x.name_your_price">
                          <ac-bound-field
                              field-type="ac-price-field" :field="orderForm.fields.named_price" label="Price" :persistent-hint="true"
                              :hint="`Enter the price you'd like to pay for this work.${currentPrice && ` Must be at least ${currentPrice.toFixed(2)} to cover the artist's costs.`}`"
                          />
                        </v-col>
                      </v-row>
                    </v-stepper-content>
                    <v-stepper-content step="2">
                      <v-row class="justify-center">
                        <v-col cols="12" sm="6" order="2" order-sm="1" class="align-self-center pt-5">
                          <ac-bound-field
                              :field="orderForm.fields.details" field-type="ac-editor" label="Description"
                              :rows="7"
                              :save-indicator="false"
                          />
                        </v-col>
                        <v-col cols="12" sm="6" order="1" order-sm="2">
                          <v-row>
                            <v-col class="d-flex justify-content justify-center align-content-center" cols="5" style="flex-direction: column">
                              <v-img src="/static/images/laptop.png" max-height="30vh" :contain="true" />
                            </v-col>
                            <v-col cols="7">
                              <h2>Example description</h2>
                              Vulpy:<br />
                              * is a fox<br />
                              * is about three feet tall<br />
                              * has orange fur, with white on his belly, cheeks, 'socks', and inner ears<br />
                              * has a paintbrush tail that can be any color, but is black for this piece.<br />
                              * has pink pawpads<br /><br />
                              Please draw Vulpy sitting and typing away excitedly on a computer!
                            </v-col>
                          </v-row>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" order="3">
                          <ac-bound-field
                              field-type="ac-uppy-file"
                              uppy-id="uppy-new-order"
                              :field="orderForm.fields.references"
                              :max-number-of-files="10"
                              label="(Optional) Add some reference images!"
                              :persistent-hint="true"
                              :persist="true"
                          ></ac-bound-field>
                        </v-col>
                      </v-row>
                    </v-stepper-content>
                    <v-stepper-content step="3">
                      <v-row v-if="invoicing">
                        <v-col cols="12">
                          <v-card>
                            <v-card-text>
                              <p><span class="title">When you hit 'Create Invoice'...</span></p>
                              <p>You will be brought to an order page, where you can then adjust terms/line items and
                                finalize once ready. Once finalized, the invoice will be sent to the customer
                                (if you provided a username or email).
                              </p>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row v-else>
                        <v-col cols="12">
                          <v-alert type="warning" :value="true" v-if="product.x.wait_list">
                            This order will be waitlisted. Waitlisted orders are not guaranteed to be accepted on any
                            particular time table and may not be fulfilled in the order they are received. Please check the
                            product description for further details or contact the artist if there is any confusion.
                            <strong>You will not be expected to pay for this order unless and until it is accepted.</strong>
                          </v-alert>
                          <v-alert type="info" :value="true">
                            Once your order is placed, the artist will review your request, make any adjustments to the quote as needed, and present them for your approval and payment. We will update you via email as things progress.
                          </v-alert>
                        </v-col>
                        <v-col cols="12">
                          <ac-load-section :controller="subjectHandler.artistProfile">
                            <template v-slot:default>
                              <v-subheader v-if="subjectHandler.artistProfile.x.commission_info">Commission Info</v-subheader>
                              <ac-rendered :value="subjectHandler.artistProfile.x.commission_info" :truncate="500" />
                            </template>
                          </ac-load-section>
                        </v-col>
                        <v-col cols="12">
                          <v-alert type="info" :value="true">
                            All orders are bound by the
                            <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement.</router-link>
                          </v-alert>
                        </v-col>
                        <v-col cols="12" v-if="product.escrow_enabled || !product.x.escrow_upgradable">
                          <ac-escrow-label :escrow="product.x.escrow_enabled" name="product" />
                        </v-col>
                        <template v-else>
                          <v-col cols="12" sm="6">
                            <ac-escrow-label :escrow="product.x.escrow_enabled" :upgrade-available="true" name="product" />
                          </v-col>
                          <v-col cols="6">
                            <ac-bound-field
                                :field="orderForm.fields.escrow_upgrade" field-type="v-checkbox" :label="shieldUpgradeLabel"
                            />
                          </v-col>
                        </template>
                      </v-row>
                    </v-stepper-content>
                  </v-stepper-items>
                </v-stepper>
                <v-card-actions row wrap>
                  <v-spacer></v-spacer>
                  <v-btn @click.prevent="orderForm.step -= 1" v-if="orderForm.step > 1" color="secondary" class="previous-button">Previous</v-btn>
                  <v-btn @click.prevent="orderForm.step += 1" v-if="orderForm.step < 3" color="primary" class="next-button" :disabled="nextDisabled">Next</v-btn>
                  <v-btn type="submit" v-if="orderForm.step === 3" color="primary" class="submit-button">
                    <span v-if="invoicing">
                      Create Invoice
                    </span>
                    <span v-else>
                      Agree and Place Order
                    </span>
                  </v-btn>
                </v-card-actions>
              </v-card>
              <v-card>
                <v-card-text>
                  <v-row no-gutters>
                  </v-row>
                </v-card-text>
              </v-card>
            </ac-form-container>
          </ac-form>
        </v-col>
        <v-col cols="12" offset-md="1" md="3" lg="2">
          <v-toolbar dense color="black">
            <ac-avatar :user="product.x.user" :show-name="false" />
            <v-toolbar-title class="ml-1"><ac-link :to="profileLink(product.x.user)">{{username}}</ac-link></v-toolbar-title>
          </v-toolbar>
          <v-card :color="$vuetify.theme.currentTheme.darkBase.darken2">
            <v-card-text>
              <v-row dense>
                <v-col class="title" cols="12" >
                  Order Summary
                </v-col>
                <v-col class="subheading" cols="12" >
                  {{product.x.name}}
                </v-col>
                <v-col cols="12">
                  <ac-asset :asset="product.x.primary_submission" thumb-name="thumbnail" />
                </v-col>
                <v-col class="subtitle-1" cols="12" v-if="product.x.name_your_price">
                  Name your price!
                </v-col>
                <v-col class="subtitle-1" cols="12" v-else>
                  Starts at ${{currentPrice.toFixed(2)}}
                  <p v-if="shielded">
                    <small>(${{product.x.starting_price.toFixed(2)}} + ${{shieldCost.toFixed(2)}} shield fee)</small>
                  </p>
                </v-col>
                <v-col>
                  <span v-if="product.x.revisions">
                    <strong>{{product.x.revisions}}</strong> revision<span v-if="product.x.revisions > 1">s</span> included.
                  </span>
                </v-col>
                <v-col cols="12">
                  <span>Estimated completion: <strong>{{formatDateTerse(deliveryDate)}}</strong></span>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {FormController} from '@/store/forms/form-controller'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import ProductCentric from '@/components/views/product/mixins/ProductCentric'
import AcAsset from '@/components/AcAsset.vue'
import Formatting from '@/mixins/formatting'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import Order from '@/types/Order'
import {User} from '@/store/profiles/types/User'
import {Watch, Prop} from 'vue-property-decorator'
import AcRendered from '@/components/wrappers/AcRendered'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Product from '@/types/Product'
import {artCall} from '@/lib/lib'
import {Character} from '@/store/characters/types/Character'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
  @Component({
    components: {
      AcEscrowLabel,
      AcLink,
      AcForm,
      AcRendered,
      AcFormContainer,
      AcAvatar,
      AcAsset,
      AcBoundField,
      AcLoadSection,
      AcFormDialog,
    },
  })
export default class NewOrder extends mixins(ProductCentric, Formatting) {
    public orderForm: FormController = null as unknown as FormController
    public loginForm: FormController = null as unknown as FormController
    public initCharacters: Character[] = []
    public showCharacters = false
    // Nasty hack, see nextDisabled for application.
    public clickCounter = 0

    @Watch('viewer.guest_email')
    public updateEmail(newVal: string) {
      if (!newVal) {
        return
      }
      this.orderForm.fields.email.update(newVal)
    }

    @Prop({default: false})
    public invoiceMode!: boolean

    @Watch('product.x')
    public trackCart(newProduct: null|Product, oldProduct: null|Product) {
      if (!newProduct) {
        return
      }
      this.orderForm.fields.rating.model = Math.min(newProduct.max_rating, this.orderForm.fields.rating.value)
    }

    @Watch('orderForm.step')
    public updateRoute(val: number) {
      this.$router.replace({params: {stepId: `${val}`}})
    }

    public submitAction() {
      if (this.orderForm.step < 3) {
        this.orderForm.step += 1
        return
      }
      this.orderForm.submitThen(this.goToOrder)
    }

    public goToOrder(order: Order) {
      // Could take a while. Let's not make it look like we're done.
      this.orderForm.sending = true
      const link = {...order.default_path}
      link.query = {...link.query, showConfirm: 'true'}
      if (!this.isRegistered) {
        link.params!.username = this.rawViewerName
        this.viewerHandler.refresh().then(() => {
          this.$router.push(link)
          this.orderForm.sending = false
        })
        return
      }
      // Special case override for table events.
      if ((this.product.x?.table_product && this.isStaff) || this.invoicing) { // eslint-disable-line camelcase
        link.query.view_as = 'Seller'
        link.name = 'SaleDeliverablePayment'
        delete link.query.showConfirm
      }
      this.$router.push(link)
      this.orderForm.sending = false
    }

    public get nextDisabled() {
      // Touch the order form so this is re-evaluated whenever it changes.
      // Just checking the email field isn't enough since Vue can't listen for it.
      // eslint-disable-next-line no-unused-expressions
      this.clickCounter
      const element = document.querySelector('#field-newOrder__email')
      if (!element) {
        return false
      }
      return document.activeElement && document.activeElement.id === element.id
    }

    public get currentPrice() {
      const product = this.product.x
      if (!product) {
        return NaN
      }
      if (this.shielded) {
        return product.shield_price
      }
      return product.starting_price
    }

    public get ratingHint() {
      if (this.invoicing) {
        return 'Please select the desired content rating of the piece being commissioned.'
      }
      return 'Please select the desired content rating of the piece you are commissioning.'
    }

    public get invoicing() {
      return this.isCurrent || (this.isStaff && this.invoiceMode)
    }

    public get shielded() {
      const product = this.product.x
      if (!product) {
        return false
      }
      if (product.escrow_enabled) {
        return true
      }
      return (product.escrow_upgradable && this.orderForm.fields.escrow_upgrade.value)
    }

    public get shieldCost() {
      const product = this.product.x
      if (!product) {
        return 0
      }
      return product.shield_price - product.starting_price
    }

    public get shieldUpgradeLabel() {
      const product = this.product.x
      if (!product) {
        return 'Add Shield Protection'
      }
      const text = 'Add Shield Protection for '
      return text + `$${this.shieldCost.toFixed(2)}`
    }

    public get privateHint() {
      if (this.invoicing) {
        return 'Mark if the client has requested that this piece be private-- which means that it will not be publicly ' +
            'shown, and copyright will be assigned to them by default (if applicable and legally possible, and your ' +
            'commission info in your artist settings does not explicitly say otherwise). You are advised to upcharge ' +
            'for this if you do it.'
      } else {
        return 'Hides the resulting submission from public view and tells the artist you want this commission ' +
          'to be private. The artist may charge an additional fee, since they will not be able to use the piece ' +
          'in their portfolio.'
      }
    }

    public get forceShield() {
      return !!({...this.$route.query}.forceShield)
    }

    public created() {
      // The way we're constructed allows us to avoid refetching if we arrive through the product page, but
      // leaves us in the same scroll position as we were. Fix that here.
      window.scrollTo(0, 0)
      this.product.get()
      const viewer = this.viewer as User
      let step = parseInt(this.$route.params.stepId) || 1
      if (step > 3) {
        step = 3
      } else if (step < 1) {
        step = 1
      }
      const validators = [{name: 'email'}]
      if (this.invoiceMode) {
        validators.pop()
      }
      this.orderForm = this.$getForm('newOrder', {
        endpoint: this.product.endpoint + 'order/',
        persistent: true,
        step,
        fields: {
          email: {value: (viewer.guest_email || ''), step: 1, validators: validators},
          private: {value: false, step: 1},
          characters: {value: [], step: 2},
          rating: {value: 0, step: 2},
          details: {value: '', step: 2},
          references: {value: [], step: 2},
          invoicing: {value: false, step: 3},
          named_price: {value: null, step: 1},
          // Note: There are agreements and warnings to display on step 3 even if there aren't fields,
          // so if this field gets moved to a lower step, a dummy field should be created for step 3 to persist.
          escrow_upgrade: {value: this.forceShield, step: 3},
        },
      })
      this.orderForm.fields.invoicing.update(this.invoicing)
      // Might be overwritten and set false if the form already exists and the visited another product.
      if (this.forceShield) {
        this.orderForm.fields.escrow_upgrade.model = true
      }
      // Since we allow the form to persist, we want to make sure if the user moves to another product, we update the
      // endpoint.
      this.orderForm.endpoint = this.product.endpoint + 'order/'
      this.subjectHandler.artistProfile.get().then()
      if (this.orderForm.fields.characters.value.length === 0) {
        this.showCharacters = true
      } else {
        const promises = []
        for (const charId of this.orderForm.fields.characters.model) {
          promises.push(artCall({url: `/api/profiles/data/character/id/${charId}/`, method: 'get'}).then(
            (response) => this.initCharacters.push(response),
          ).catch(() => {
            this.orderForm.fields.characters.model = this.orderForm.fields.characters.model.filter(
              (val: number) => val !== charId,
            )
          }))
        }
        Promise.all(promises).then(() => { this.showCharacters = true })
      }
    }
}
</script>
