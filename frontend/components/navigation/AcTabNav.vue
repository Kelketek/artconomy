<template>
  <v-container fluid class="pa-0">
    <v-tabs grow centered show-arrows class="hidden-sm-and-down">
      <ac-tab
        v-for="item in items"
        :key="item.title"
        :to="item.value"
        :count="item.count"
        :icon="item.icon"
        :tag="tagFor(item)"
      >
        {{ item.title }}
      </ac-tab>
    </v-tabs>
    <v-select
      v-model="tab"
      :items="items"
      :label="label"
      :prepend-inner-icon="tab && tab.icon"
      class="hidden-md-and-up"
      :item-text="renderText"
    />
  </v-container>
</template>

<script setup lang="ts">
import { RouteLocationRaw, useRoute, useRouter } from "vue-router"
import AcTab from "@/components/AcTab.vue"
import { computed } from "vue"
import type { TabNavSpec } from "@/types/main"

const route = useRoute()
const router = useRouter()
const props = withDefaults(
  defineProps<{ label: string; items: TabNavSpec[]; headingLevel?: number }>(),
  { headingLevel: 0 },
)

const renderText = (item: TabNavSpec) => {
  if (item.count) {
    return `${item.title} (${item.count})`
  }
  return item.title
}

const tagFor = (item: TabNavSpec) => {
  if (!props.headingLevel) {
    return "span"
  }
  if (item === tab.value) {
    return `h${props.headingLevel}`
  }
  return "span"
}

const tab = computed({
  get() {
    return props.items.filter(
      (item) =>
        route.matched.filter((match) => match.name === item.value.name).length,
    )[0] as TabNavSpec
  },
  set(val) {
    router.replace(val as RouteLocationRaw)
  },
})
</script>
