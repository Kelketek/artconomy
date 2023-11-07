<template>
  <v-form v-bind="$attrs">
    <slot/>
  </v-form>
</template>

<script lang="ts">
import {Component, toNative, Vue} from 'vue-facing-decorator'

@Component({inheritAttrs: false})
class AcForm extends Vue {
  public mounted() {
    this.$nextTick(() => {
      // @ts-ignore
      window._paq.push(['FormAnalytics::scanForForms', this.$el])
    })
  }
}

export default toNative(AcForm)
</script>
