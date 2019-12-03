<template>
  <v-form v-bind="$attrs" v-on="$listeners"><slot /></v-form>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'

@Component({inheritAttrs: false})
export default class AcForm extends Vue {
  public mounted() {
    this.$nextTick(() => {
      // @ts-ignore
      window._paq.push(['FormAnalytics::scanForForms', this.$el])
    })
  }
}
</script>
