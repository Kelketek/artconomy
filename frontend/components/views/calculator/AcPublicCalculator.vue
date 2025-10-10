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
              :disabled="escrowDisabled"
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
            />
            <small :class="{ faded: escrowDisabled }"
              >How many orders protected by Artconomy Shield you expect to have
              on average each month.</small
            >
          </v-col>
          <v-col cols="12" md="4">
            <v-number-input
              v-model="nonEscrowCount"
              :min="0"
              label="Unshielded Commission count"
            />
            <small
              >How many orders per month you want to track using Artconomy's
              organizational tools, but don't want us to handle payment
              for.</small
            >
          </v-col>
        </v-row>
        <v-card-title>Monthly Totals</v-card-title>
        <v-row v-if="tooMany">
          <v-col cols="12">
            <v-alert type="warning"
              >Cannot calculate totals. The {{ selectedPlan }} plan can only
              support up to {{ maxSimultaneous }} {{ noun }} at a time.</v-alert
            >
          </v-col>
        </v-row>
        <v-row v-else>
          <v-col cols="6" md="4" offset-md="2">
            <v-card-subtitle>Total earned</v-card-subtitle>
            ${{ totalProcessed }}
          </v-col>
          <v-col cols="6" md="4">
            <v-card-subtitle>Tracking Fees</v-card-subtitle>
            ${{ trackingFees }}
            <div><small>Added to your monthly invoice</small></div>
          </v-col>
          <v-col cols="6" md="4" offset-md="2">
            <v-card-subtitle>Processing Fees</v-card-subtitle>
            ${{ processingFees }}
            <div>
              <small>Paid by client, included in commission price</small>
            </div>
          </v-col>
          <v-col cols="6" md="4">
            <v-card-subtitle>Total Fees</v-card-subtitle>
            ${{ totalFees }}
            <div>
              <small
                >All fees paid between you and your clients for Artconomy's
                services</small
              >
            </div>
          </v-col>
          <v-col cols="6" md="4" offset-md="2">
            <v-card-subtitle>Monthly Subscription Fee</v-card-subtitle>
            ${{ monthlySubscriptionFee }}
            <div><small>Added to your monthly invoice</small></div>
          </v-col>
          <v-col cols="6" md="4">
            <v-card-subtitle>Monthly invoice total</v-card-subtitle>
            ${{ invoiceAmount }}
            <div>
              <small>Total amount charged to your card each month</small>
            </div>
          </v-col>
          <v-col cols="12" class="text-center">
            <v-card-title
              >Recommended Plan:
              <strong>{{ recommendedPlan }}</strong></v-card-title
            >
          </v-col>
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
  ServicePlan,
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
import { MODIFIER_TYPE_SETS } from "@/components/price_preview/mixins/line_items.ts"

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

const planMap: Record<string, ServicePlan> = {}
pricing.plans.forEach((plan) => {
  planMap[plan.name] = plan
})

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
  tooMany: boolean
  maxSimultaneous: number
  totalEarned: string
  processingFees: string
  trackingFees: string
  totalFees: string
  invoiceAmount: string
  monthlySubscriptionFee: string
}

const tallies = computed(() => {
  const results: { [key: string]: Tallies } = {}
  for (const [name, controller] of listControllerMaps) {
    const plan = pricing.plans.filter((plan) => plan.name === name)[0]
    const totals = getTotals(controller.list.map((x) => x.x!))
    const earningsLines = controller.list
      .filter((x) => x.x!.destination_user_id)
      .map((x) => x.x!)
    const totalEarned = multiply([
      sum(earningsLines.map((x) => totals.subtotals.get(x)!)),
      escrowCount.value + "",
    ])
    const processingFeeLines = controller.list
      .filter((x) => MODIFIER_TYPE_SETS.has(x.x!.type))
      .map((x) => x.x!)
    const processingFees = multiply([
      sum(processingFeeLines.map((x) => totals.subtotals.get(x)!)),
      escrowCount.value + "",
    ])
    const trackingFees = multiply([
      plan.per_deliverable_price,
      nonEscrowCount.value + "",
    ])
    let tooMany: boolean
    const maxSimultaneous = plan.max_simultaneous_orders
    if (maxSimultaneous) {
      tooMany = escrowCount.value + nonEscrowCount.value > maxSimultaneous
    } else {
      tooMany = false
    }
    const monthlySubscriptionFee = plan.monthly_charge
    results[name] = {
      tooMany,
      maxSimultaneous,
      totalEarned,
      processingFees,
      monthlySubscriptionFee,
      trackingFees,
      totalFees: sum([processingFees, trackingFees, monthlySubscriptionFee]),
      invoiceAmount: sum([trackingFees, plan.monthly_charge]),
    }
  }
  return results
})

const currentValue = (entry: keyof Tallies) => {
  return () => {
    if (!selectedPlan.value) {
      return "0"
    }
    return tallies.value[selectedPlan.value][entry]
  }
}

const totalProcessed = computed(currentValue("totalEarned"))
const processingFees = computed(currentValue("processingFees"))
const trackingFees = computed(currentValue("trackingFees"))
const totalFees = computed(currentValue("totalFees"))
const invoiceAmount = computed(currentValue("invoiceAmount"))
const tooMany = computed(currentValue("tooMany"))
const maxSimultaneous = computed(currentValue("maxSimultaneous"))
const monthlySubscriptionFee = computed(currentValue("monthlySubscriptionFee"))
const noun = computed(() => (maxSimultaneous.value === 1 ? "order" : "orders"))

const recommendedPlan = computed(() => {
  const totalOrders = escrowCount.value + nonEscrowCount.value
  const possibilities = pricing.plans.filter(
    (plan) =>
      !plan.max_simultaneous_orders ||
      plan.max_simultaneous_orders >= totalOrders,
  )
  let planName = "Unknown"
  let amount = Infinity
  for (const possibility of possibilities) {
    const candidateAmount = parseFloat(
      tallies.value[possibility.name].totalFees,
    )
    if (candidateAmount < amount) {
      planName = possibility.name
      amount = candidateAmount
    }
  }
  return planName
})
</script>

<style scoped>
.faded {
  opacity: 0.25;
}
</style>
