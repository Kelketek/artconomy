<template>
  <router-link v-bind="$props" v-if="to && !newTab" :to="to" @click.capture="navigate">
    <slot/>
  </router-link>
  <a :href="`${to}`" v-else-if="newTab && to" target="_blank">
    <slot/>
  </a>
  <slot v-else/>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {RouteLocationRaw} from 'vue-router'
import {ArtVue} from '@/lib/lib'

@Component
class AcLink extends ArtVue {
  @Prop()
  public to!: RouteLocationRaw

  // Must be used with string location
  @Prop({default: false})
  public newTab!: boolean

  public navigate(event: Event) {
    event.preventDefault()
    if (this.$store.state.iFrame) {
      event.stopPropagation()
      const routeData = this.$router.resolve(this.to)
      window.open(routeData.href, '_blank')
      return
    }
    this.$router.push(this.to)
  }
}

export default toNative(AcLink)
</script>
