<template>
  <fragment>
    <router-link v-bind="$props" v-if="to" @click.native.capture="navigate"><slot></slot></router-link>
    <slot v-else></slot>
  </fragment>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Fragment} from 'vue-fragment'
import {Prop} from 'vue-property-decorator'
import {Route} from 'vue-router'
import {State} from 'vuex-class'

@Component({components: {Fragment}})
export default class AcLink extends Vue {
    @Prop()
    public to!: Route
    @State('iFrame') public iFrame!: boolean

    public navigate(event: Event) {
      if (this.iFrame) {
        const routeData = this.$router.resolve(this.to)
        window.open(routeData.href, '_blank')
        event.stopPropagation()
        event.preventDefault()
        return
      }
      this.$router.push(this.to)
    }
}
</script>
