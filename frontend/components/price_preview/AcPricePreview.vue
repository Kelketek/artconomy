<template>
  <ac-load-section ref="el" :controller="pricing" class="py-2">
    <ac-load-section :controller="subjectHandler.user">
      <template #default>
        <ac-load-section
          v-if="!!pricing.x"
          :controller="lineItems"
          class="compact-fields"
        >
          <template #default>
            <template v-if="editable && editBase">
              <ac-line-item-editor
                v-for="(line, index) in baseItems"
                :key="line.x!.id"
                :line="line"
                :price-data="priceData"
                :disabled="disabled"
                :editing="editable"
                :enable-new-line="
                  index === baseItems.length - 1 && !addOns.length
                "
                @new-line="postSubmitAdd(addOnForm)"
              />
            </template>
            <template v-else>
              <ac-line-item-preview
                v-for="line in baseItems"
                :key="line.x!.id"
                :line="line.x!"
                :price-data="priceData"
                :editing="editable"
                :transfer="transfer"
              />
            </template>
            <template v-if="editable">
              <ac-line-item-editor
                v-for="(line, index) in addOns"
                :key="line.x!.id"
                :line="line"
                :price-data="priceData"
                :editing="editable"
                :disabled="disabled"
                :enable-new-line="index === addOns.length - 1"
                @new-line="postSubmitAdd(addOnForm)"
              />
              <ac-new-line-skeleton v-if="addOnForm.sending" />
              <ac-form-container v-bind="addOnForm.bind" :show-spinner="false">
                <ac-form @submit.prevent="postSubmitAdd(addOnForm)">
                  <ac-new-line-item :form="addOnForm" />
                </ac-form>
              </ac-form-container>
            </template>
            <template v-else>
              <ac-line-item-preview
                v-for="line in addOns"
                :key="line.x!.id"
                :line="line.x!"
                :price-data="priceData"
                :transfer="transfer"
              />
            </template>
            <ac-line-item-preview
              v-for="line in modifiers"
              :key="line.id"
              :line="line"
              :price-data="priceData"
              :editing="editable"
              :transfer="transfer"
            />
            <template v-if="editable && powers.table_seller">
              <ac-line-item-editor
                v-for="(line, index) in extras"
                :key="line.x!.id"
                :line="line"
                :price-data="priceData"
                :editing="editable"
                :disabled="disabled"
                :enable-new-line="index === extras.length - 1"
                @new-line="postSubmitAdd(extraForm)"
              />
              <ac-new-line-skeleton v-if="extraForm.sending" />
              <ac-form-container v-bind="extraForm.bind" :show-spinner="false">
                <ac-form
                  @submit.prevent="extraForm.submitThen(lineItems.uniquePush)"
                >
                  <ac-new-line-item :form="extraForm" />
                </ac-form>
              </ac-form-container>
            </template>
            <template v-else>
              <ac-line-item-preview
                v-for="line in extras"
                :key="line.x!.id"
                :line="line.x!"
                :price-data="priceData"
              />
            </template>
            <ac-line-item-preview
              v-for="line in taxes"
              :key="line.id"
              :line="line"
              :price-data="priceData"
              :editing="editable"
              :transfer="transfer"
            />
            <v-row no-gutters>
              <v-col class="text-right pr-1" cols="6">
                <strong v-if="transfer">Total Charge:</strong>
                <strong v-else>Total Price:</strong>
              </v-col>
              <v-col class="text-left pl-1" cols="6">
                <v-chip v-if="isSeller" color="blue" variant="flat">
                  ${{ rawPrice }}
                </v-chip>
                <span v-else>${{ rawPrice }}</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col v-if="isSeller && escrow" class="text-right pr-1" cols="6">
                <strong>Your Payout:</strong>
              </v-col>
              <v-col
                v-if="isSeller && escrow"
                class="text-left pl-1"
                align-self="center"
                cols="6"
              >
                <v-chip color="green" variant="flat">
                  <strong>${{ payout }}</strong>
                </v-chip>
              </v-col>
              <v-col v-if="isSeller && !hideHourlyForm" cols="12" md="6">
                <ac-bound-field
                  :field="hourlyForm.fields.hours"
                  type="number"
                  label="If I worked for this many hours..."
                  min="0"
                  step="1"
                />
              </v-col>
              <v-col
                v-if="isSeller"
                cols="12"
                :class="{ transparent: !hourly }"
                :aria-hidden="!hourly"
              >
                I would earn <strong>${{ hourly }}/hour.</strong>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </template>
    </ac-load-section>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { totalForTypes } from "@/lib/lineItemFunctions.ts"
import AcLineItemPreview from "@/components/price_preview/AcLineItemPreview.vue"
import { LineType } from "@/types/enums/LineType.ts"
import { ListController } from "@/store/lists/controller.ts"
import AcLineItemEditor from "@/components/price_preview/AcLineItemEditor.vue"
import { FormController } from "@/store/forms/form-controller.ts"
import AcNewLineItem from "@/components/price_preview/AcNewLineItem.vue"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcForm from "@/components/wrappers/AcForm.vue"
import AcNewLineSkeleton from "@/components/price_preview/AcNewLineSkeleton.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { useLineItems } from "@/components/price_preview/mixins/line_items.ts"
import { computed, nextTick, ref } from "vue"
import { usePricing } from "@/mixins/PricingAware.ts"
import { useSubject } from "@/mixins/subjective.ts"
import { useViewer } from "@/mixins/viewer.ts"
import type { LineItem, LineTypeValue, SubjectiveProps } from "@/types/main"

const props = withDefaults(
  defineProps<
    {
      lineItems: ListController<LineItem>
      isSeller?: boolean
      escrow?: boolean
      editable?: boolean
      editBase?: boolean
      hideHourlyForm?: boolean
      transfer?: boolean
      // Disables inputs, such as when performing another operation
      disabled?: boolean
    } & SubjectiveProps
  >(),
  {
    escrow: true,
    editable: false,
    editBase: false,
    hideHourlyForm: false,
    transfer: false,
    disabled: false,
  },
)

const { subjectHandler } = useSubject({ props })
const { powers } = useViewer()

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

const hourlyForm = useForm("hourly", {
  endpoint: "#",
  fields: { hours: { value: null } },
})

const hourly = computed(() => {
  const hours = hourlyForm.fields.hours.model || 0
  if (hours === 0) {
    return ""
  }
  let currentPrice = rawPrice.value
  if (props.escrow) {
    currentPrice = payout.value
  }
  try {
    return (parseFloat(currentPrice) / hours).toFixed(2)
  } catch {
    return ""
  }
})

const payout = computed(() => {
  const types = [LineType.BASE_PRICE, LineType.ADD_ON, LineType.TIP]
  return totalForTypes(priceData.value, types)
})

const MODIFIER_TYPE_SETS = new Set([
  LineType.TIP,
  LineType.SHIELD,
  LineType.BONUS,
  LineType.TABLE_SERVICE,
  LineType.PROCESSING,
  LineType.DELIVERABLE_TRACKING,
  LineType.RECONCILIATION,
] as LineTypeValue[])

const moddedItems = computed(() => {
  // Modify the items for user-facing calculation.
  if (props.isSeller) {
    return rawLineItems.value
  }
  // We eliminate the Deliverable tracking fee since that's just for the artist's reference-- it doesn't affect
  // the price charged. It just tells the artist what they will be charged later.
  return rawLineItems.value.filter(
    (line: LineItem) =>
      !([LineType.DELIVERABLE_TRACKING] as LineTypeValue[]).includes(line.type),
  )
})

const taxes = computed(() =>
  moddedItems.value.filter((line: LineItem) => line.type === LineType.TAX),
)

const modifiers = computed(() =>
  moddedItems.value.filter(
    // We include tips here since we will handle that with a different interface.
    (line: LineItem) => MODIFIER_TYPE_SETS.has(line.type),
  ),
)

const { pricing } = usePricing()

const el = ref<typeof AcLoadSection | null>(null)

const postSubmitAdd = (form: FormController) => {
  form.submitThen(props.lineItems.uniquePush).then(() => {
    const line = props.lineItems.list[props.lineItems.list.length - 1]
    nextTick(() => {
      const element = el.value?.$el.querySelector(
        `#lineItem-${line.x!.id}-description`,
      ) as HTMLElement
      element.focus()
    })
  })
}
</script>

<style scoped>
.transparent {
  opacity: 0;
}
</style>
