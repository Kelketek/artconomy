<template>
  <div></div>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer'

@Component
class ViewerComponent extends mixins(Viewer) {
}
export default toNative(ViewerComponent)
</script>
