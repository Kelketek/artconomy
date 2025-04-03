<script setup lang="ts">
/*
This module is used for cases where our setup hooks won't work unless the data is available.
 */
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { usePricing } from "@/mixins/PricingAware.ts"

const { pricing } = usePricing()
</script>

<template>
  <ac-load-section :controller="pricing">
    <template #default>
      <slot :pricing="pricing.x!"></slot>
    </template>
  </ac-load-section>
</template>

<style scoped></style>
