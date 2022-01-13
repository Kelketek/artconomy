import Vue from 'vue'
import LineItem from '@/types/LineItem'
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import {Component, Prop} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import {FormController} from '@/store/forms/form-controller'

@Component
export default class LineItemMixin extends Vue {
  @Prop({required: true})
  public lineItems!: ListController<LineItem>

  @Prop({default: false})
  public editBase!: boolean

  @Prop({default: false})
  public editExtras!: boolean

  @Prop({default: false})
  public editable!: boolean

  public addOnForm: FormController = null as unknown as FormController
  public extraForm: FormController = null as unknown as FormController

  public get rawPrice() {
    return this.priceData.total
  }

  public get priceData() {
    return getTotals(this.moddedPlusForms)
  }

  public get moddedPlusForms() {
    return this.addForms(this.moddedItems)
  }

  public get rawPlusForms() {
    return this.addForms(this.rawLineItems)
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

  public get rawLineItems() {
    return this.lineItems.list.map((item) => item.x as LineItem)
  }

  public get moddedItems() {
    // Override this if you need to consolidate some of the line items for display, such as showing
    // shield as a monolith rather than breaking down which parts are bonus and which are normal fees.
    //
    // Note that these are not controllers, but the raw LineItems. Avoid using this when items need to be edited.
    return this.rawLineItems
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

  public linesOfType(type: LineTypes) {
    return this.lineItems.list.filter((item) => item.x!.type === type)
  }

  public get addOns() {
    return this.linesOfType(LineTypes.ADD_ON)
  }

  public get extras() {
    return this.linesOfType(LineTypes.EXTRA)
  }

  public get taxes() {
    return this.linesOfType(LineTypes.TAX)
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

  public created() {
    this.addOnForm = this.$getForm(`${this.lineItems.name}_addOn`, {
      endpoint: this.lineItems.endpoint,
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        description: {value: ''},
        type: {value: LineTypes.ADD_ON},
        percentage: {value: 0},
      },
    })
    this.extraForm = this.$getForm(`${this.lineItems.name}_extra`, {
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
