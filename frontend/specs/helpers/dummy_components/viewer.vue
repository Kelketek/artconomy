<template>
  <div></div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'

  @Component
export default class ViewerComponent extends mixins(Viewer) {
}
</script>
