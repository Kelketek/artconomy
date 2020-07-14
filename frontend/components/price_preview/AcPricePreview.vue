<template>
  <ac-load-section :controller="pricing">
    <template v-slot:default>
      <ac-load-section :controller="lineItems" v-if="validPrice" class="compact-fields">
        <template v-slot:default>
          <template v-if="editable && editBase">
            <ac-line-item-editor :line="line" v-for="line in baseItems" :key="line.x.id" :price-data="priceData" :editing="editable" />
          </template>
          <template v-else>
            <ac-line-item-preview :line="line.x" v-for="line in baseItems" :key="line.x.id" :price-data="priceData" :editing="editable" />
          </template>
          <template v-if="editable">
            <ac-line-item-editor :line="line" v-for="line in addOns" :key="line.x.id" :price-data="priceData" :editing="editable" />
            <ac-form-container v-bind="addOnForm.bind">
              <ac-form @submit.prevent="addOnForm.submitThen(lineItems.push)">
                <ac-new-line-item :form="addOnForm" :price="priceData.map.get(addOnFormItem) || 0" />
              </ac-form>
            </ac-form-container>
          </template>
          <template v-else>
            <ac-line-item-preview :line="line.x" v-for="line in addOns" :key="line.x.id" :price-data="priceData" />
          </template>
          <ac-line-item-preview :line="line" v-for="line in modifiers" :key="line.id" :price-data="priceData" :editing="editable" />
          <template v-if="editable && isStaff">
            <ac-line-item-editor :line="line" v-for="line in extras" :key="line.x.id" :price-data="priceData" :editing="editable" />
            <ac-form-container v-bind="extraForm.bind">
              <ac-form @submit.prevent="extraForm.submitThen(lineItems.push)">
                <ac-new-line-item :form="extraForm" :price="priceData.map.get(extraFormItem) || 0" />
              </ac-form>
            </ac-form-container>
          </template>
          <template v-else>
            <ac-line-item-preview :line="line.x" v-for="line in extras" :key="line.x.id" :price-data="priceData" />
          </template>
          <ac-line-item-preview :line="line" v-for="line in taxes" :key="line.id" :price-data="priceData" :editing="editable" />
          <v-row no-gutters>
            <v-col class="text-right pr-1" cols="6" ><strong>Total Price:</strong></v-col>
            <v-col class="text-left pl-1" cols="6" >${{rawPrice.toFixed(2)}}</v-col>
          </v-row>
          <v-row>
            <v-col class="text-right pr-1" cols="6" v-if="isSeller && escrow"><strong>Your Payout:</strong></v-col>
            <v-col class="text-left pl-1" align-self="center" cols="6" v-if="isSeller && escrow"><strong>${{payout.toFixed(2)}}</strong></v-col>
            <v-col v-if="isSeller" cols="12" md="6">
              <v-text-field v-model="hours" type="number" label="If I worked for this many hours..." min="0" step="1"></v-text-field>
            </v-col>
            <v-col v-if="isSeller && hourly" cols="12" md="6">
              I would earn <strong>${{hourly}}/hour.</strong>
            </v-col>
          </v-row>
          <v-row v-if="isSeller && escrow && !landscape">
            <v-col class="text-center" cols="12">
              You could earn <strong>${{bonus.toFixed(2)}}</strong> more with
              <router-link :to="{name: 'Upgrade'}">Artconomy Landscape</router-link>!
            </v-col>
          </v-row>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Subjective from '../../mixins/subjective'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {getTotals, totalForTypes, sum} from '@/lib/lineItemFunctions'
import LineItem from '@/types/LineItem'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import {LineTypes} from '@/types/LineTypes'
import {ListController} from '@/store/lists/controller'
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import {FormController} from '@/store/forms/form-controller'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import Big from 'big.js'
import {flatten} from '@/lib/lib'

@Component({
  components: {AcForm, AcFormContainer, AcNewLineItem, AcLineItemEditor, AcLineItemPreview, AcLoadSection},
})
export default class AcPricePreview extends mixins(Subjective) {
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
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

  public hours = null

  public get rawPrice() {
    return this.priceData.total
  }

  public get priceData() {
    return getTotals(this.moddedPlusForms)
  }

  public get payout() {
    const types = [LineTypes.BASE_PRICE, LineTypes.ADD_ON]
    if (this.landscape) {
      types.push(LineTypes.BONUS)
    }
    return totalForTypes(this.priceData, types)
  }

  public get hourly() {
    const hours = this.hours || 0
    let currentPrice = this.rawPrice
    if (this.escrow) {
      currentPrice = this.payout
    }
    try {
      return currentPrice.div(Big(hours)).round(2, 0) + ''
    } catch {
      return ''
    }
  }

  public get rawLineItems() {
    return this.lineItems.list.map((item) => item.x as LineItem)
  }

  public get bonus() {
    return totalForTypes(getTotals(this.rawPlusForms), [LineTypes.BONUS])
  }

  public get baseItems() {
    return this.lineItems.list.filter(item => item.x && item.x.type === LineTypes.BASE_PRICE)
  }

  public get modifiers() {
    return this.moddedItems.filter(
      // We include tips here since we will handle that with a different interface.
      (line: LineItem) => [
        LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE,
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
    if (this.isSeller && this.landscape) {
      return this.rawLineItems
    }
    const toConsolidate = this.rawLineItems.filter(
      (line: LineItem) => [LineTypes.SHIELD, LineTypes.BONUS].includes(line.type),
    )
    const modded = this.rawLineItems.filter(
      (line: LineItem) => (![LineTypes.SHIELD, LineTypes.BONUS].includes(line.type)),
    )
    if (toConsolidate.length) {
      const consolidated = {
        id: -10,
        amount: parseFloat(sum(toConsolidate.map((line: LineItem) => Big(line.amount))).toFixed(2)),
        percentage: parseFloat(sum(toConsolidate.map((line: LineItem) => Big(line.percentage))).toFixed(2)),
        type: LineTypes.SHIELD,
        priority: 300,
        description: '',
        back_into_percentage: false,
        cascade_percentage: true,
        cascade_amount: true,
      }
      modded.push(consolidated)
    }
    return modded
  }

  public get addOnFormItem(): LineItem {
    return {
      id: -105,
      amount: parseFloat(this.addOnForm.fields.amount.value),
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

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
    this.pricing.get()
    this.addOnForm = this.$getForm(flatten(`${this.lineItems.name}/addOn`), {
      endpoint: this.lineItems.endpoint,
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        description: {value: ''},
        type: {value: LineTypes.ADD_ON},
        percentage: {value: 0},
      },
    })
    this.extraForm = this.$getForm(flatten(`${this.lineItems.name}/extra`), {
      endpoint: this.lineItems.endpoint,
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        description: {value: ''},
        type: {value: LineTypes.EXTRA},
        percentage: {value: 0},
      },
    })
  }
}
</script>
