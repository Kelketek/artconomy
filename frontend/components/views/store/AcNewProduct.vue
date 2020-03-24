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
                        field-type="v-checkbox"
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
                  <v-col cols="12" sm="6" >
                    <ac-bound-field :field="newProduct.fields.base_price" label="List Price"
                                    field-type="ac-price-field"
                                    :hint="priceHint"

                    />
                  </v-col>
                  <v-col cols="12" sm="6" >
                    <ac-price-preview
                      :username="username" :line-items="lineItems" v-if="escrow"
                    />
                  </v-col>
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
                </v-row>
              </v-stepper-content>
              <v-stepper-content :step="3">
                <v-row>
                  <v-col cols="12" sm="6">
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
import LineItem from '@/types/LineItem'
import {LineTypes} from '@/types/LineTypes'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'

@Component({components: {AcPricePreview, AcBoundField, AcPatchField, AcLoadSection, AcFormDialog}})
export default class AcNewProduct extends Subjective {
    public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
    @Prop({required: true})
    public value!: boolean
    public newProduct: FormController = null as unknown as FormController

    public get url() {
      return `/api/sales/v1/account/${this.username}/products/`
    }

    public get limitAtOnce() {
      return this.newProduct.fields.max_parallel.value !== 0
    }

    public get lineItems() {
      const linesController = this.$getList('newProductLines', {endpoint: '????', paginated: false})
      linesController.ready = true
      if (!(this.pricing.x)) {
        linesController.setList([])
        return linesController
      }
      const basePrice = parseFloat(this.newProduct.fields.base_price.value)
      if (isNaN(basePrice)) {
        linesController.setList([])
        return linesController
      }
      const lines: LineItem[] = [{
        id: -1,
        priority: 0,
        type: LineTypes.BASE_PRICE,
        amount: basePrice,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      }]
      if (this.newProduct.fields.table_product.value) {
        lines.push({
          id: -2,
          priority: 400,
          type: LineTypes.TABLE_SERVICE,
          cascade_percentage: true,
          cascade_amount: false,
          amount: this.pricing.x.table_static,
          percentage: this.pricing.x.table_percentage,
          back_into_percentage: false,
          description: '',
        }, {
          id: -3,
          priority: 700,
          type: LineTypes.TAX,
          cascade_percentage: true,
          cascade_amount: true,
          back_into_percentage: true,
          percentage: this.pricing.x.table_tax,
          description: '',
          amount: 0,
        })
      } else if (this.escrow && basePrice > 0) {
        lines.push({
          id: -4,
          priority: 300,
          type: LineTypes.SHIELD,
          cascade_percentage: true,
          cascade_amount: true,
          amount: this.pricing.x.standard_static,
          percentage: this.pricing.x.standard_percentage,
          back_into_percentage: false,
          description: '',
        }, {
          id: -5,
          priority: 300,
          type: LineTypes.BONUS,
          cascade_percentage: true,
          cascade_amount: true,
          back_into_percentage: false,
          amount: this.pricing.x.premium_static_bonus,
          percentage: this.pricing.x.premium_percentage_bonus,
          description: '',
        })
      }
      linesController.setList(lines)
      return linesController
    }

    public set limitAtOnce(val: boolean) {
      const field = this.newProduct.fields.max_parallel
      if (val) {
        field.update(field.value || 1)
      } else {
        field.update(0)
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
        {name: 'Product', params: {username: this.username, productId: product.id + ''}, query: {editing: 'true'}}
      )
    }

    public created() {
      this.subjectHandler.artistProfile.get().catch(this.setError)
      this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
      this.pricing.get()
      this.newProduct = this.$getForm(`${this.username}__newProduct`, {
        endpoint: this.url,
        fields: {
          name: {value: ''},
          description: {value: ''},
          base_price: {value: '25.00', step: 2, validators: [{name: 'numeric'}]},
          expected_turnaround: {value: 5, step: 2, validators: [{name: 'numeric'}]},
          task_weight: {value: 1, step: 3},
          revisions: {value: 1, step: 2},
          max_parallel: {value: 0, step: 3},
          hidden: {value: false},
          table_product: {value: false},
          tags: {value: []},
        },
      })
    }
}
</script>
