<template>
  <ac-load-section :controller="pricing" class="py-2">
    <ac-load-section :controller="subjectHandler.user">
      <template v-slot:default>
        <ac-load-section :controller="lineItems" v-if="validPrice" class="compact-fields">
          <template v-slot:default>
            <template v-if="editable && editBase">
              <ac-line-item-editor
                  :line="line" v-for="(line, index) in baseItems"
                  :key="line.x!.id"
                  :price-data="priceData"
                  :disabled="disabled"
                  :editing="editable"
                  @new-line="postSubmitAdd(addOnForm)"
                  :enable-new-line="(index === baseItems.length - 1) && !addOns.length"
              />
            </template>
            <template v-else>
              <ac-line-item-preview :line="line.x" v-for="line in baseItems" :key="line.x!.id" :price-data="priceData"
                                    :editing="editable" :transfer="transfer"/>
            </template>
            <template v-if="editable">
              <ac-line-item-editor
                  :line="line" v-for="(line, index) in addOns"
                  :key="line.x!.id"
                  :price-data="priceData"
                  :editing="editable"
                  :disabled="disabled"
                  @new-line="postSubmitAdd(addOnForm)"
                  :enable-new-line="index === addOns.length - 1"
              />
              <ac-new-line-skeleton v-if="addOnForm.sending"/>
              <ac-form-container v-bind="addOnForm.bind" :show-spinner="false">
                <ac-form @submit.prevent="postSubmitAdd(addOnForm)">
                  <ac-new-line-item :form="addOnForm"/>
                </ac-form>
              </ac-form-container>
            </template>
            <template v-else>
              <ac-line-item-preview :line="line.x" v-for="line in addOns" :key="line.x!.id" :price-data="priceData"
                                    :transfer="transfer"/>
            </template>
            <ac-line-item-preview :line="line" v-for="line in modifiers" :key="line.id" :price-data="priceData"
                                  :editing="editable" :transfer="transfer"/>
            <template v-if="editable && isStaff">
              <ac-line-item-editor
                  :line="line"
                  v-for="(line, index) in extras"
                  :key="line.x!.id"
                  :price-data="priceData"
                  :editing="editable"
                  :disabled="disabled"
                  @new-line="postSubmitAdd(extraForm)"
                  :enable-new-line="index === extras.length - 1"/>
              <ac-new-line-skeleton v-if="extraForm.sending"/>
              <ac-form-container v-bind="extraForm.bind" :show-spinner="false">
                <ac-form @submit.prevent="extraForm.submitThen(lineItems.uniquePush)">
                  <ac-new-line-item :form="extraForm"/>
                </ac-form>
              </ac-form-container>
            </template>
            <template v-else>
              <ac-line-item-preview :line="line.x" v-for="line in extras" :key="line.x!.id" :price-data="priceData"/>
            </template>
            <ac-line-item-preview :line="line" v-for="line in taxes" :key="line.id" :price-data="priceData"
                                  :editing="editable" :transfer="transfer"/>
            <v-row no-gutters>
              <v-col class="text-right pr-1" cols="6">
                <strong v-if="transfer">Total Charge:</strong>
                <strong v-else>Total Price:</strong>
              </v-col>
              <v-col class="text-left pl-1" cols="6">
                <v-chip color="blue" variant="flat" v-if="isSeller">${{rawPrice.toFixed(2)}}</v-chip>
                <span v-else>${{rawPrice.toFixed(2)}}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="text-right pr-1" cols="6" v-if="isSeller && escrow">
                <strong>Your Payout:</strong>
              </v-col>
              <v-col class="text-left pl-1" align-self="center" cols="6" v-if="isSeller && escrow">
                <v-chip color="green" variant="flat"><strong>${{payout.toFixed(2)}}</strong></v-chip>
              </v-col>
              <v-col cols="12" md="6" v-if="isSeller && !hideHourlyForm">
                <ac-bound-field :field="hourlyForm.fields.hours" type="number"
                                label="If I worked for this many hours..." min="0" step="1"/>
              </v-col>
              <v-col v-if="isSeller" cols="12" :class="{transparent: !hourly}" :aria-hidden="!hourly">
                I would earn <strong>${{hourly}}/hour.</strong>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </template>
    </ac-load-section>
  </ac-load-section>
</template>

<style scoped>
.transparent {
  opacity: 0;
}
</style>

<script lang="ts">
import Subjective from '../../mixins/subjective.ts'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import Pricing from '@/types/Pricing.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions.ts'
import LineItem from '@/types/LineItem.ts'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import {LineTypes} from '@/types/LineTypes.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import {Decimal} from 'decimal.js'
import AcNewLineSkeleton from '@/components/price_preview/AcNewLineSkeleton.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'

@Component({
  components: {
    AcPatchField,
    AcBoundField,
    AcNewLineSkeleton,
    AcForm,
    AcFormContainer,
    AcNewLineItem,
    AcLineItemEditor,
    AcLineItemPreview,
    AcLoadSection,
  },
})
class AcPricePreview extends mixins(Subjective) {
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public hourlyForm: FormController = null as unknown as FormController
  public addOnForm: FormController = null as unknown as FormController
  public extraForm: FormController = null as unknown as FormController
  @Prop({required: true})
  public lineItems!: ListController<LineItem>

  @Prop({default: true})
  public isSeller!: boolean

  @Prop({default: true})
  public escrow!: boolean

  @Prop({default: false})
  public editable!: boolean

  @Prop({default: false})
  public editBase!: boolean

  @Prop({default: false})
  public hideHourlyForm!: boolean

  @Prop({default: false})
  public transfer!: boolean

  // Disables inputs, such as when performing another operation
  @Prop({default: false})
  public disabled!: boolean

  public hours = null

  public get rawPrice() {
    return this.priceData.total
  }

  public get priceData() {
    return getTotals(this.moddedPlusForms)
  }

  public get payout() {
    const types = [LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.TIP]
    return totalForTypes(this.priceData, types)
  }

  public get hourly() {
    const hours = this.hourlyForm.fields.hours.model || 0
    if (hours === 0) {
      return ''
    }
    let currentPrice = this.rawPrice
    if (this.escrow) {
      currentPrice = this.payout
    }
    try {
      return currentPrice.div(new Decimal(hours)).toDP(2, Decimal.ROUND_DOWN) + ''
    } catch {
      return ''
    }
  }

  public get rawLineItems() {
    return this.lineItems.list.map((item) => item.x as LineItem)
  }

  public get baseItems() {
    return this.lineItems.list.filter(item => item.x && item.x.type === LineTypes.BASE_PRICE)
  }

  public get modifiers() {
    return this.moddedItems.filter(
        // We include tips here since we will handle that with a different interface.
        (line: LineItem) => [
          LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE, LineTypes.PROCESSING,
          LineTypes.DELIVERABLE_TRACKING, LineTypes.RECONCILIATION,
        ].includes(line.type))
  }

  public get addOns() {
    return this.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.ADD_ON)
  }

  public get extras() {
    return this.lineItems.list.filter((item) => item.x && item.x.type === LineTypes.EXTRA)
  }

  public get taxes() {
    return this.moddedItems.filter((line: LineItem) => line.type === LineTypes.TAX)
  }

  public get moddedItems() {
    // Modify the items for user-facing calculation.
    if (this.isSeller) {
      return this.rawLineItems
    }
    // We eliminate the Deliverable tracking fee since that's just for the artist's reference-- it doesn't affect
    // the price charged. It just tells the artist what they will be charged later.
    return this.rawLineItems.filter(
        (line: LineItem) => (![LineTypes.DELIVERABLE_TRACKING].includes(line.type)),
    )
  }

  public get addOnFormItem(): LineItem {
    return {
      id: -105,
      amount: parseFloat(this.addOnForm.fields.amount.value),
      frozen_value: null,
      cascade_amount: false,
      cascade_percentage: false,
      back_into_percentage: false,
      percentage: parseFloat(this.addOnForm.fields.percentage.value),
      type: this.addOnForm.fields.type.value,
      priority: 100,
      description: this.addOnForm.fields.description.value,
    }
  }

  public get extraFormItem(): LineItem {
    return {
      id: -106,
      amount: parseFloat(this.extraForm.fields.amount.value),
      frozen_value: null,
      cascade_amount: false,
      cascade_percentage: false,
      back_into_percentage: false,
      percentage: parseFloat(this.extraForm.fields.percentage.value),
      type: this.extraForm.fields.type.value,
      priority: 400,
      description: this.extraForm.fields.description.value,
    }
  }

  public addForms(startingItems: LineItem[]) {
    const allItems = [...startingItems]
    const addOnValue = parseFloat(this.addOnForm.fields.amount.value)
    if (addOnValue && !isNaN(addOnValue)) {
      allItems.push(this.addOnFormItem)
    }
    const extraValue = parseFloat(this.extraForm.fields.amount.value)
    if (extraValue && !isNaN(extraValue)) {
      allItems.push(this.extraFormItem)
    }
    return allItems
  }

  public get moddedPlusForms() {
    return this.addForms(this.moddedItems)
  }

  public get rawPlusForms() {
    return this.addForms(this.rawLineItems)
  }

  public get validPrice() {
    /* istanbul ignore if */
    if (!this.pricing.x) {
      return false
    }
    return true
  }

  public postSubmitAdd(form: FormController) {
    form.submitThen(this.lineItems.uniquePush).then(() => {
      const line = this.lineItems.list[this.lineItems.list.length - 1]
      this.$nextTick(() => {
        const element = this.$el.querySelector(`#lineItem-${line.x!.id}-description`) as HTMLElement
        element.focus()
      })
    })
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get()
    this.addOnForm = this.$getForm(`${this.lineItems.name.value}_addOn`, {
      endpoint: this.lineItems.endpoint,
      fields: {
        amount: {
          value: 0,
          validators: [{name: 'numeric'}],
        },
        description: {value: ''},
        type: {value: LineTypes.ADD_ON},
        percentage: {value: 0},
      },
    })
    this.extraForm = this.$getForm(`${this.lineItems.name.value}_extra`, {
      endpoint: this.lineItems.endpoint,
      fields: {
        amount: {
          value: 0,
          validators: [{name: 'numeric'}],
        },
        description: {value: ''},
        type: {value: LineTypes.EXTRA},
        percentage: {value: 0},
      },
    })
    this.hourlyForm = this.$getForm('hourly', {
      endpoint: '#',
      fields: {hours: {value: null}},
    })
  }
}

export default toNative(AcPricePreview)
</script>
