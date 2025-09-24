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
          <v-col cols="12" sm="6">
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
          <v-col cols="12" sm="6">
            <v-checkbox
              v-model="escrowDisabled"
              label="My country isn't listed"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <ac-price-field
              v-model="price"
              :disabled="escrowDisabled"
              label="Average take-home amount"
            />
          </v-col>
          <v-col v-if="!escrowDisabled" cols="12">
            <ac-price-comparison
              ref="priceComparison"
              :username="viewer.username"
              :line-item-set-maps="lineItemSetMaps"
              :disabled="escrowDisabled"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-number-input
              v-model="rawEscrowCount"
              :disabled="escrowDisabled"
              :min="0"
              label="Shielded Commission count"
              :persistent-hint="true"
              hint="How many orders protected by Artconomy Shield you expect to have on average each month."
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-number-input
              v-model="nonEscrowCount"
              :min="0"
              label="Unshielded Commission count"
              :persistent-hint="true"
              hint="How many orders per month you want to track using Artconomy's organizational tools, but don't want us to handle payment for."
            />
          </v-col>
          <v-col cols="12" sm="6">
            {{ international }}
          </v-col>
          <v-col cols="12" sm="6">
            {{ nonEscrowCount }}
          </v-col>
          <v-col cols="12" sm="6">
            {{ escrowCount }}
          </v-col>
          <v-col cols="12" sm="6">
            {{ listControllerMaps.keys() }}
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
} from "@/types/main"
import AcPriceField from "@/components/fields/AcPriceField.vue"
import { useList } from "@/store/lists/hooks.ts"
import { deliverableLines } from "@/lib/lineItemFunctions.ts"
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
watch(
  () => priceComparison.value?.tab.value,
  (value) => {
    console.log(value)
  },
  { immediate: true, deep: true },
)

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
        escrowEnabled: true,
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
</script>

<style scoped>
.faded {
  opacity: 0.3;
}
</style>
