<template>
  <v-col v-observe-visibility="grower">
    <ac-loading-spinner
      v-if="list.fetching && list.currentPage > 1"
      :min-height="minHeight"
    />
  </v-col>
</template>

<script setup lang="ts">
import AcLoadingSpinner from './wrappers/AcLoadingSpinner.vue'
import {ListController} from '@/store/lists/controller.ts'
import {ref, watch} from 'vue'
import {ObserveVisibility as vObserveVisibility} from 'vue-observe-visibility'

declare interface AcGrowSpinnerProps {
  minHeight?: string,
  list: ListController<any>
}
const props = withDefaults(defineProps<AcGrowSpinnerProps>(), {minHeight: '3rem'})
const visible = ref(false)
const grower = (val: boolean) => {
  visible.value = val
  props.list.grower(val)
}
watch(() => props.list.fetching, (val: boolean) => {
  if (!val) {
    grower(visible.value)
  }
})
watch(() => props.list.moreAvailable, (val: boolean) => {
  if (val) {
    props.list.grower(visible.value)
  }
}, {immediate: true})
</script>
