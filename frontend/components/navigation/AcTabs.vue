<template>
  <v-container
    fluid
    class="pa-0"
  >
    <v-tabs
      v-model="tab"
      grow
      centered
      show-arrows
      class="hidden-sm-and-down"
    >
      <ac-tab
        v-for="item in items"
        :key="item.title"
        :count="item.count"
        :icon="item.icon"
        :value="item.value"
      >
        {{ item.title }}
      </ac-tab>
    </v-tabs>
    <v-select
      v-model="tab"
      :items="items"
      :label="label"
      :prepend-inner-icon="(tabSpec && tabSpec.icon) || ''"
      class="hidden-md-and-up"
      :item-text="renderText"
    />
  </v-container>
</template>

<script setup lang="ts">
import AcTab from '@/components/AcTab.vue'
import {computed} from 'vue'
import type {TabSpec} from '@/types/main'

const props = defineProps<{modelValue: number, label: string, items: TabSpec[]}>()
const emit = defineEmits<{'update:modelValue': [number]}>()

const tab = computed({
  get() {
    return props.modelValue
  },
  set(val: number) {
    emit('update:modelValue', val)
  }
})

const renderText = (item: TabSpec) => {
  if (item.count) {
    return `${item.title} (${item.count})`
  }
  return item.title
}

const tabSpec = computed(() => {
  return props.items[tab.value]
})
</script>
