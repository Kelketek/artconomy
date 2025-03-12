<template>
  <ac-load-section :controller="cards">
    <template #default>
      <div class="flex card-group-container">
        <v-radio-group
          :hide-details="true"
          :model-value="modelValue"
          @update:model-value="sendInput"
        >
          <ac-card
            v-for="card in cards.list"
            :key="card.x!.id"
            :card="card"
            :card-list="cards"
            :value="modelValue"
            :field-mode="true"
          />
        </v-radio-group>
      </div>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcCard from "@/components/views/settings/payment/AcCard.vue"
import { ListController } from "@/store/lists/controller.ts"

import type { CreditCardToken } from "@/types/main"

defineProps<{
  modelValue: number | null
  cards: ListController<CreditCardToken>
}>()
const emit = defineEmits<{ "update:modelValue": [number | null] }>()
const sendInput = (value: number | null) => emit("update:modelValue", value)
</script>

<style>
.card-group-container .v-input--radio-group .v-input__control {
  width: 100%;
}
</style>
