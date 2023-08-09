<template>
  <ac-form-dialog
      :value="value"
      @input="toggle"
      :large="true"
      :fluid="true"
      title="New Product"
      @submit.prevent="newProduct.submitThen(goToProduct)"
      v-bind="newProduct.bind"
  >
    <template slot="top-buttons" />
    <ac-load-section :controller="subjectHandler.artistProfile">
      <template v-slot:default>
        <v-col>
          <v-row no-gutters v-if="subjectHandler.artistProfile.x.bank_account_status === 0">
            <v-col class="pt-2" cols="12" md="8" offset-md="2" >
              <ac-patch-field :patcher="subjectHandler.artistProfile.patchers.bank_account_status" field-type="ac-bank-toggle" :username="username" />
            </v-col>
          </v-row>
          <v-stepper v-model="newProduct.step" class="submission-stepper" v-else>
            <v-stepper-header>
              <v-stepper-step :complete="newProduct.steps[1].complete" :step="1" @click="newProduct.step = 1" :rules="newProduct.steps[1].rules">Basics</v-stepper-step>
              <v-divider />
              <v-stepper-step :complete="newProduct.steps[2].complete" :step="2" @click="newProduct.step = 2" :rules="newProduct.steps[2].rules">Terms</v-stepper-step>
              <v-divider />
              <v-stepper-step :step="3" @click="newProduct.step = 3" :rules="newProduct.steps[3].rules">Workload</v-stepper-step>
            </v-stepper-header>
            <v-stepper-items>
              <v-stepper-content :step="1">
                <v-row>
                  <v-col cols="12" sm="6" order="1" order-sm="1" >
                    <ac-bound-field
                        :field="newProduct.fields.name" label="Product Name"
                        hint="Pick a helpful name to describe what you're selling, such as 'Reference Sheet' or 'Line Drawing'."
                    />
                  </v-col>
                  <v-col cols="12" sm="6" order="3" order-sm="2" >
                    <ac-bound-field
                        :field="newProduct.fields.hidden" label="Hide Product"
                        field-type="ac-checkbox"
                        :persistent-hint="true"
                        hint="This product will not be immediately available. You will need to unhide the product in order for customers to order." />
                  </v-col>
                  <v-col cols="12" order="2" order-sm="3" >
                    <ac-bound-field
                        :field="newProduct.fields.tags" label="Tags"
                        field-type="ac-tag-field"
                        hint="Add some tags to make it easy to search for your product."
                    />
                  </v-col>
                  <v-col cols="12" order="4" order-sm="4" >
                    <ac-bound-field
                        :field="newProduct.fields.description" label="Description"
                        field-type="ac-editor" :save-indicator="false"
                        hint="Describe what you are offering. Remember that if you have general commission terms of service, you
                    can add these in your artist settings, and they will show on every product, so just include a
                    description of the product itself here." />
                  </v-col>
                </v-row>
              </v-stepper-content>
              <v-stepper-content :step="2">
                <v-row>
                  <v-col cols="12" md="6" lg="4">
                    <v-row>
                      <v-col cols="12" sm="6" lg="12">
                        <ac-bound-field :field="newProduct.fields.base_price" :label="basePriceLabel"
                                        field-type="ac-price-field"
                                        :hint="priceHint"
                        />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <ac-bound-field
                            :field="newProduct.fields.cascade_fees" field-type="v-switch" label="Absorb fees" :persistent-hint="true"
                            hint="If turned on, the price you set is the price your commissioner will see, and you
                            will pay all fees from that price. If turned off, the price you set is the amount you
                            take home, and the total the customer pays includes the fees."
                            :true-value="true"
                            :false-value="false"
                        />
                      </v-col>
                      <v-col cols="12" sm="6" v-if="escrow">
                        <ac-bound-field
                            :field="newProduct.fields.escrow_enabled"
                            field-type="v-switch"
                            label="Shield enabled"
                            :persistent-hint="true"
                            hint="Enable shield protection for this product."
                            :true-value="true"
                            :false-value="false"
                        />
                      </v-col>
                      <v-col cols="12" sm="6" v-if="escrow">
                        <ac-bound-field
                            :field="newProduct.fields.escrow_upgradable"
                            field-type="v-switch"
                            label="Allow Shield Upgrade"
                            :persistent-hint="true"
                            :disabled="newProduct.fields.escrow_enabled.value"
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
                    <ac-bound-field
                        :field="newProduct.fields.name_your_price" field-type="v-switch" label="Name Your Price" :persistent-hint="true"
                        hint="If turned on, the base price is treated as a minimum price to cover costs,
                                     and the client is prompted to put in their own price. This is useful for 'Pay
                                     What You Want' commissions. You should note whatever impact the price has on the
                                     commission in the product details in order to avoid any dispute issues."
                        :true-value="true"
                        :false-value="false"
                    />
                  </v-col>
                  <v-col cols="12" sm="6" v-if="subject.paypal_configured">
                    <ac-bound-field
                        :field="newProduct.fields.paypal"
                        field-type="v-switch"
                        label="PayPal Invoicing"
                        :persistent-hint="true"
                        hint="If the order is marked unshielded, generate a PayPal invoice upon acceptance."
                        :true-value="true"
                        :false-value="false"
                    />
                  </v-col>
                  <v-col sm="6" v-else-if="$vuetify.breakpoint.smAndUp"></v-col>
                  <v-col cols="12" sm="6" >
                    <ac-bound-field :field="newProduct.fields.expected_turnaround" number
                                    label="Expected Days Turnaround"
                                    hint="How many standard business days you expect this task to take (on average)."
                                    :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12" sm="6" >
                    <ac-bound-field :field="newProduct.fields.revisions" number
                                    label="Included Revisions"
                                    hint="How many revisions you're offering with this product. This does not include final
                                      delivery-- only intermediate WIP steps."
                                    :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12">
                    <ac-bound-field :field="newProduct.fields.max_rating" label="Maximum Content Rating" field-type="ac-rating-field" />
                  </v-col>
                </v-row>
              </v-stepper-content>
              <v-stepper-content :step="3">
                <v-row>
                  <v-col cols="12">
                    <h2>AWOO Workload Settings</h2>
                    <v-divider />
                    <p>You can set these settings to help the Artconomy Workdload Organization and Overview tool manage your workload for you.</p>
                    <p><strong>If you're not sure what to do here, or would like to set these settings later, the defaults should be safe.</strong></p>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <ac-bound-field :field="newProduct.fields.task_weight" number
                                    label="Slots"
                                    hint="How many slots an order of this product should take up. If this task is
                                        particularly big, you may want it to take up more than one slot."
                                    :persistent-hint="true"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <ac-bound-field :field="newProduct.fields.wait_list"
                                    label="Wait List Product"
                                    field-type="ac-checkbox"
                                    :disabled="!subject.landscape"
                                    hint="Marks this product as a waitlist product. Orders will be put in your
                                        waitlist queue which is separate from your normal order queue. You should specify
                                        your waitlist policy in the product description or in your commission info.
                                        This setting takes precedence over all other workload settings."
                                    :persistent-hint="true"
                    />
                    <div v-if="!subject.landscape">
                      This feature only available for <router-link :to="{name: 'Upgrade'}">Landscape</router-link> subscribers.
                    </div>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-checkbox v-model="limitAtOnce" :persistent-hint="true"
                                label="Limit Availability"
                                hint="If you would like to make sure you're never doing more than a few of these at a time, check this box."
                    />
                  </v-col>
                  <v-col cols="12" sm="6" v-if="limitAtOnce">
                    <ac-bound-field :persistent-hint="true"
                                    :field="newProduct.fields.max_parallel"
                                    type="number"
                                    label="Maximum at Once"
                                    min="1"
                                    hint="If you already have this many orders of this product, don't allow customers to order any more."
                    />
                  </v-col>
                </v-row>
              </v-stepper-content>
            </v-stepper-items>
          </v-stepper>
        </v-col>
      </template>
    </ac-load-section>
    <template slot="bottom-buttons">
      <v-card-actions row wrap v-if="subjectHandler.artistProfile.x && subjectHandler.artistProfile.x.bank_account_status !== 0">
        <v-spacer />
        <v-btn @click.prevent="toggle(false)">Cancel</v-btn>
        <v-btn @click.prevent="newProduct.step -= 1" v-if="newProduct.step > 1" color="secondary">Previous</v-btn>
        <v-btn @click.prevent="newProduct.step += 1" v-if="newProduct.step < 3" color="primary">Next</v-btn>
        <v-btn type="submit" v-if="newProduct.step === 3" color="primary" class="submit-button" :disabled="newProduct.sending">Submit</v-btn>
      </v-card-actions>
      <v-card-actions v-else>
        <v-spacer />
        <v-btn @click.prevent="toggle(false)">Cancel</v-btn>
      </v-card-actions>
    </template>
  </ac-form-dialog>
</template>
<script lang="ts">
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import Subjective from '@/mixins/subjective'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import {FormController} from '@/store/forms/form-controller'
import Product from '@/types/Product'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import {flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import {deliverableLines} from '@/lib/lineItemFunctions'
import AcPriceComparison from '@/components/price_preview/AcPriceComparison.vue'
import {LineItemSetMap} from '@/types/LineItemSetMap'

@Component({
  components: {
    AcPriceComparison,
    AcPricePreview,
    AcBoundField,
    AcPatchField,
    AcLoadSection,
    AcFormDialog,
  },
})
export default class AcNewProduct extends Subjective {
    public pricing = null as unknown as SingleController<Pricing>
    @Prop({required: true})
    public value!: boolean

    public newProduct = null as unknown as FormController

    public get url() {
      return `/api/sales/account/${this.username}/products/`
    }

    public get limitAtOnce() {
      return this.newProduct.fields.max_parallel.value !== 0
    }

    public get lineItemSetMaps(): LineItemSetMap[] {
      const sets = []
      const escrowLinesController = this.$getList('newProductLinesEscrow', {
        endpoint: '#',
        paginated: false,
      })
      const nonEscrowLinesController = this.$getList('newProductLinesNonEscrow', {
        endpoint: '#',
        paginated: false,
      })
      const preferredLinesController = this.$getList('newProductPreferredPlanItems', {
        endpoint: '#',
        paginated: false,
      })
      const pricing = this.pricing.x
      const basePrice = parseFloat(this.newProduct.fields.base_price.value)
      // eslint-disable-next-line camelcase
      const planName = this.subject?.service_plan
      const international = !!this.subject?.international
      const cascade = this.newProduct.fields.cascade_fees.value
      const tableProduct = this.newProduct.fields.table_product.value
      let appendPreferred = false
      const options = {
        basePrice,
        cascade: cascade && (this.newProduct.fields.escrow_enabled.value),
        international,
        pricing,
        escrowEnabled: true,
        tableProduct,
        extraLines: [],
      }
      if (this.escrow && (this.newProduct.fields.escrow_enabled.value || this.newProduct.fields.escrow_upgradable.value)) {
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
      if (!this.escrow || !this.newProduct.fields.escrow_enabled.value) {
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

    public set limitAtOnce(val: boolean) {
      const field = this.newProduct.fields.max_parallel
      if (val) {
        field.update(field.value || 1)
      } else {
        field.update(0)
      }
    }

    public get basePriceLabel() {
      if (this.newProduct.fields.cascade_fees.model) {
        return 'List Price'
      } else {
        return 'Take home amount'
      }
    }

    public get escrow() {
      const profile = this.subjectHandler.artistProfile.x
      return profile && profile.bank_account_status === 1
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

    public toggle(value: boolean) {
      this.$emit('input', value)
    }

    public goToProduct(product: Product) {
      this.$router.push(
        {name: 'Product', params: {username: this.username, productId: product.id + ''}, query: {editing: 'true'}},
      )
    }

    public created() {
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
      this.pricing.get()
      this.newProduct = this.$getForm(`${flatten(this.username)}__newProduct`, {
        endpoint: this.url,
        fields: {
          name: {value: ''},
          description: {value: ''},
          base_price: {value: '25.00', step: 2, validators: [{name: 'numeric'}]},
          expected_turnaround: {value: 5, step: 2, validators: [{name: 'numeric'}]},
          max_rating: {value: Ratings.GENERAL, step: 2},
          wait_list: {value: false},
          task_weight: {value: 1, step: 3},
          revisions: {value: 1, step: 2},
          max_parallel: {value: 0, step: 3},
          hidden: {value: false},
          table_product: {value: false},
          tags: {value: []},
          cascade_fees: {value: false, step: 2},
          escrow_enabled: {value: true, step: 2},
          escrow_upgradable: {value: false, step: 2},
          paypal: {value: true, step: 2},
          name_your_price: {value: false, step: 2},
        },
      })
    }
}
</script>
