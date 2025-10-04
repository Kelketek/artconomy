<template>
  <v-container>
    <v-card>
      <v-card-title> Calculator </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            Check this calendar to see which plan is right for you! All fees are
            included in the prices.
          </v-col>
          <v-col cols="12" sm="6" md="4" offset-md="2">
            <v-select
              v-if="stripeCountries.x"
              v-model="country"
              field-type="v-select"
              outlined
              :disabled="escrowDisabled"
              label="Select your country"
              :items="stripeCountries.x.countries"
            />
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-checkbox
              v-model="escrowDisabled"
              label="My country isn't listed"
            />
          </v-col>
          <v-col cols="12" sm="6" offset-sm="3">
            <ac-price-field
              v-model="price"
              label="Average take-home amount per commission"
            />
          </v-col>
          <v-col cols="12" md="6" offset-md="3">
            <ac-price-comparison
              ref="priceComparison"
              :username="viewer.username"
              :line-item-set-maps="lineItemSetMaps"
              :disabled="escrowDisabled"
            />
          </v-col>
          <v-col cols="12" md="4" offset-md="2">
            <v-number-input
              v-model="rawEscrowCount"
              :disabled="escrowDisabled"
              :min="0"
              label="Shielded Commission count"
              :persistent-hint="true"
              hint="How many orders protected by Artconomy Shield you expect to have on average each month."
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-number-input
              v-model="nonEscrowCount"
              :min="0"
              label="Unshielded Commission count"
              :persistent-hint="true"
              hint="How many orders per month you want to track using Artconomy's organizational tools, but don't want us to handle payment for."
            />
          </v-col>
        </v-row>
        <v-card-title>Totals</v-card-title>
        <v-row>
          <v-col>Total amount processed: ${{ totalProcessed }}</v-col>
          <v-col>Tracking Fees: ${{ trackingFees }}</v-col>
          <v-col>Processing Fees: ${{ processingFees }}</v-col>
          <v-col>Total Fees: ${{ totalFees }}</v-col>
          <v-col>Monthly invoice total: ${{ invoiceAmount }}</v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, ComputedRef, Ref } from "vue"
import { useSingle } from "@/store/singles/hooks.ts"
import {
  LineItem,
  Pricing,
  RawLineItemSetMap,
  StripeCountryList,
} from "@/types/main"
import AcPriceField from "@/components/fields/AcPriceField.vue"
import { useList } from "@/store/lists/hooks.ts"
import {
  deliverableLines,
  multiply,
  sum,
  getTotals,
} from "@/lib/lineItemFunctions.ts"
import { ListController } from "@/store/lists/controller.ts"
import { useViewer } from "@/mixins/viewer.ts"
import AcPriceComparison from "@/components/price_preview/AcPriceComparison.vue"

// Non-reactive. We need to keep the keys we get during setup.
const { pricing } = defineProps<{ pricing: Pricing }>()

const listControllerMaps = new Map(
  pricing.plans.map((servicePlan) => [
    servicePlan.name,
    useList<LineItem>(`calculator${servicePlan.name}`, {
      endpoint: "#",
      paginated: false,
    }),
  ]),
)
// const planNames = pricing.plans.map((servicePlan) => servicePlan.name)
const { viewer } = useViewer()
const priceComparison: Ref<null | typeof AcPriceComparison> = ref(null)
const selectedPlan = computed(() => {
  if (!priceComparison.value) {
    return ""
  }
  return priceComparison.value.selection
})

const escrowDisabled = ref(false)
const rawEscrowCount = ref(1)
const price = ref("50.00")
const escrowCount = computed(() => {
  if (escrowDisabled.value) {
    return 0
  }
  return rawEscrowCount.value
})
const nonEscrowCount = ref(0)
const country = ref("US")
const international = computed(() => country.value !== "US")
const stripeCountries = useSingle<StripeCountryList>("stripeCountries", {
  endpoint: "/api/sales/stripe-countries/",
  persist: true,
  x: { countries: [] },
})
stripeCountries.get()

const rawLineItemSetMaps: ComputedRef<RawLineItemSetMap[]> = computed(() => {
  const sets: RawLineItemSetMap[] = []
  pricing.plans.forEach((plan) => {
    sets.push({
      name: plan.name,
      lineItems: deliverableLines({
        basePrice: price.value,
        tableProduct: false,
        escrowEnabled: !escrowDisabled.value,
        international: international.value,
        extraLines: [],
        pricing: pricing,
        planName: plan.name,
      }),
      offer: false,
    })
  })
  return sets
})

watch(
  rawLineItemSetMaps,
  (rawLineItemSetMaps: RawLineItemSetMap[]) => {
    for (const set of rawLineItemSetMaps) {
      const controller = listControllerMaps.get(
        set.name,
      ) as ListController<LineItem>
      controller.makeReady(set.lineItems)
    }
  },
  { deep: true, immediate: true },
)

const lineItemSetMaps = computed(() => {
  const sets = []
  for (const set of rawLineItemSetMaps.value) {
    const controller = listControllerMaps.get(
      set.name,
    ) as ListController<LineItem>
    sets.push({ name: set.name, lineItems: controller, offer: set.offer })
  }
  return sets
})

declare interface Tallies {
  totalProcessed: string
  processingFees: string
  trackingFees: string
  totalFees: string
  invoiceAmount: string
}

const tallies = computed(() => {
  const results: { [key: string]: Tallies } = {}
  for (const [name, controller] of listControllerMaps) {
    const totals = getTotals(controller.list.map((x) => x.x!))
    const totalProcessed = multiply([
      sum(totals.subtotals.values()),
      escrowCount.value + "",
    ])
    const processingFees = multiply(["0", "1"])
    const plan = pricing.plans.filter((plan) => plan.name === name)[0]
    const trackingFees = multiply([
      plan.per_deliverable_price,
      nonEscrowCount.value + "",
    ])
    results[name] = {
      totalProcessed,
      processingFees,
      trackingFees,
      totalFees: sum([processingFees, trackingFees]),
      invoiceAmount: sum([trackingFees, plan.monthly_charge]),
    }
  }
  return results
})

const currentValue = (entry: keyof Tallies): string => {
  return () => {
    if (!selectedPlan.value) {
      return "0"
    }
    return tallies.value[selectedPlan.value][entry]
  }
}

const totalProcessed = computed(currentValue("totalProcessed"))
const processingFees = computed(currentValue("processingFees"))
const trackingFees = computed(currentValue("trackingFees"))
const totalFees = computed(currentValue("totalFees"))
const invoiceAmount = computed(currentValue("invoiceAmount"))
</script>
