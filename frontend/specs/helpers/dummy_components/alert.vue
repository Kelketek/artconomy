<template>
  <div></div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Alerts from '@/mixins/alerts'

  @Component
export default class AlertsComponent extends mixins(Alerts) {
}
</script>
