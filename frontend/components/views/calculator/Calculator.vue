<template>
  <ac-requires-pricing>
    <template #default="{ pricing }">
      <ac-public-calculator :pricing="pricing"></ac-public-calculator>
    </template>
  </ac-requires-pricing>
</template>

<script setup lang="ts">
import AcRequiresPricing from "@/components/views/calculator/AcRequiresPricing.vue"
import AcPublicCalculator from "@/components/views/calculator/AcPublicCalculator.vue"
</script>
