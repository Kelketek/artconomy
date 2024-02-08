<template>
  <div></div>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Alerts from '@/mixins/alerts.ts'

@Component({})
class AlertsComponent extends mixins(Alerts) {
}
export default toNative(AlertsComponent)
</script>
