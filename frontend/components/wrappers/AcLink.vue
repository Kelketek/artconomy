<template>
  <fragment>
    <router-link v-bind="$props" v-if="to && !newTab" :to="to" @click.native.capture="navigate"><slot /></router-link>
    <a :href="to" v-else-if="newTab && to" target="_blank"><slot /></a>
    <slot v-else />
  </fragment>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Fragment} from 'vue-fragment'
import {Prop} from 'vue-property-decorator'
import {Location} from 'vue-router'
import {State} from 'vuex-class'

@Component({components: {Fragment}})
export default class AcLink extends Vue {
  @Prop()
  public to!: Location
  @State('iFrame') public iFrame!: boolean
  // Must be used with string location
  @Prop({default: false})
  public newTab!: boolean

  public navigate(event: Event) {
    event.preventDefault()
    if (this.iFrame) {
      event.stopPropagation()
      const routeData = this.$router.resolve(this.to)
      window.open(routeData.href, '_blank')
      return
    }
    this.$router.push(this.to)
  }
}
</script>
