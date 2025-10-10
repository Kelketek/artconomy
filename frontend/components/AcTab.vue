<template>
  <v-tab :to="destination" :value="value">
    <v-icon v-if="icon" left :icon="icon" size="large" class="mr-1" />
    <component :is="tag" class="text-button font-weight-bold">
      <template #default>
        <slot />
      </template>
    </component>
    <span v-if="count">&nbsp;({{ count }})</span>
  </v-tab>
</template>

<script setup lang="ts">
import { ListController } from "@/store/lists/controller.ts"
import { RouteLocationNamedRaw } from "vue-router"
import { computed } from "vue"
import { clone } from "@/lib/lib.ts"

declare interface TabProps {
  icon?: string
  list?: ListController<any>
  count?: number
  to?: RouteLocationNamedRaw
  value?: number
  trackPages?: boolean
  pageVariable?: string
  tag?: string
}

const props = withDefaults(defineProps<TabProps>(), {
  trackPages: true,
  pageVariable: "page",
  tag: "span",
  icon: undefined,
  list: undefined,
  count: undefined,
  to: undefined,
  value: undefined,
})

const destination = computed(() => {
  if (!props.to) {
    return undefined
  }
  if (!props.trackPages) {
    return props.to
  }
  if (!props.list) {
    return props.to
  }
  const route = clone(props.to)
  if (props.list.currentPage > 1) {
    const query = route.query || {}
    query[props.pageVariable] = props.list.currentPage + ""
    route.query = query
  }
  return route
})
</script>
