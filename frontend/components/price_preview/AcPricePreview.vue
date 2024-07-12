<template>
  <ac-load-section :controller="pricing" class="py-2" ref="el">
    <ac-load-section :controller="subjectHandler.user">
      <template v-slot:default>
        <ac-load-section :controller="lineItems" v-if="!!pricing.x" class="compact-fields">
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
              <ac-line-item-preview :line="line.x!" v-for="line in baseItems" :key="line.x!.id" :price-data="priceData"
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
              <ac-line-item-preview :line="line.x!" v-for="line in addOns" :key="line.x!.id" :price-data="priceData"
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
              <ac-line-item-preview :line="line.x!" v-for="line in extras" :key="line.x!.id" :price-data="priceData"/>
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

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {totalForTypes} from '@/lib/lineItemFunctions.ts'
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
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useLineItems} from '@/components/price_preview/mixins/line_items.ts'
import {computed, nextTick, ref} from 'vue'
import {usePricing} from '@/mixins/PricingAware.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useViewer} from '@/mixins/viewer.ts'


const props = withDefaults(defineProps<{
  lineItems: ListController<LineItem>,
  isSeller?: boolean,
  escrow?: boolean,
  editable?: boolean,
  editBase?: boolean,
  hideHourlyForm?: boolean,
  transfer?: boolean,
  // Disables inputs, such as when performing another operation
  disabled?: boolean,
} & SubjectiveProps>(), {
  escrow: true,
  editable: false,
  editBase: false,
  hideHourlyForm: false,
  transfer: false,
  disabled: false,
})

const {subjectHandler} = useSubject(props)
const {isStaff} = useViewer()

const {
  addOnForm,
  extraForm,
  rawLineItems,
  baseItems,
  addOns,
  extras,
  priceData,
  rawPrice,
} = useLineItems(props)

const hourlyForm = useForm('hourly', {
  endpoint: '#',
  fields: {hours: {value: null}},
})

const hourly = computed(() => {
  const hours = hourlyForm.fields.hours.model || 0
  if (hours === 0) {
    return ''
  }
  let currentPrice = rawPrice.value
  if (props.escrow) {
    currentPrice = payout.value
  }
  try {
    return currentPrice.div(new Decimal(hours)).toDP(2, Decimal.ROUND_DOWN) + ''
  } catch {
    return ''
  }
})

const payout = computed(() => {
  const types = [LineTypes.BASE_PRICE, LineTypes.ADD_ON, LineTypes.TIP]
  return totalForTypes(priceData.value, types)
})

const MODIFIER_TYPE_SETS = new Set([LineTypes.TIP, LineTypes.SHIELD, LineTypes.BONUS, LineTypes.TABLE_SERVICE, LineTypes.PROCESSING,
    LineTypes.DELIVERABLE_TRACKING, LineTypes.RECONCILIATION])

const moddedItems = computed(() => {
  // Modify the items for user-facing calculation.
  if (props.isSeller) {
    return rawLineItems.value
  }
  // We eliminate the Deliverable tracking fee since that's just for the artist's reference-- it doesn't affect
  // the price charged. It just tells the artist what they will be charged later.
  return rawLineItems.value.filter(
      (line: LineItem) => (![LineTypes.DELIVERABLE_TRACKING].includes(line.type)),
  )
})

const taxes = computed(() => moddedItems.value.filter((line: LineItem) => line.type === LineTypes.TAX))

const modifiers = computed(() => moddedItems.value.filter(
  // We include tips here since we will handle that with a different interface.
  (line: LineItem) => MODIFIER_TYPE_SETS.has(line.type)),
)

const {pricing} = usePricing()

const el = ref<typeof AcLoadSection|null>(null)

const postSubmitAdd = (form: FormController) => {
  form.submitThen(props.lineItems.uniquePush).then(() => {
    const line = props.lineItems.list[props.lineItems.list.length - 1]
    nextTick(() => {
      const element = el.value?.$el.querySelector(`#lineItem-${line.x!.id}-description`) as HTMLElement
      element.focus()
    })
  })
}
</script>
