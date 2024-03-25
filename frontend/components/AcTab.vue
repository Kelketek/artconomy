<template>
  <v-tab :to="destination" :value="value">
    <v-icon left v-if="icon" :icon="icon" size="large" class="mr-1"/>
    <component :is="tag" class="text-button font-weight-bold"><slot /></component>
    <span v-if="count">&nbsp;({{count}})</span>
  </v-tab>
</template>

<script setup lang="ts">
import {ListController} from '@/store/lists/controller.ts'
import cloneDeep from 'lodash/cloneDeep'
import {RouteLocationNamedRaw} from 'vue-router'
import {TabSpec} from '@/types/TabSpec.ts'
import {computed} from 'vue'

declare interface TabProps {
  icon?: string,
  list?: ListController<any>
  count?: number,
  to?: RouteLocationNamedRaw,
  value?: number,
  trackPages?: boolean,
  pageVariable?: string,
  tag?: string,
}

const props = withDefaults(defineProps<TabProps>(), {trackPages: true, pageVariable: 'page', tag: 'span'})

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
  const route = cloneDeep(props.to)
  if (props.list.currentPage > 1) {
    const query = route.query || {}
    query[props.pageVariable] = props.list.currentPage + ''
    route.query = query
  }
  return route
})
</script>
