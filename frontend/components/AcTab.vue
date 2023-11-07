<template>
  <v-tab :to="destination" :value="value">
    <v-icon left v-if="icon" :icon="icon" size="large" class="mr-1"/>
    <slot></slot>
    <span v-if="count">&nbsp;({{count}})</span>
  </v-tab>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {ListController} from '@/store/lists/controller'
import cloneDeep from 'lodash/cloneDeep'
import {RouteLocationNamedRaw, RouteLocationRaw} from 'vue-router'
import {TabSpec} from '@/types/TabSpec'

@Component
class AcTab extends Vue {
  @Prop()
  public icon!: string

  @Prop()
  public list!: ListController<any> | null

  @Prop()
  public count!: number

  @Prop()
  public to!: RouteLocationNamedRaw

  @Prop({required: false})
  public value!: TabSpec

  @Prop({default: true})
  public trackPages!: boolean

  @Prop({default: 'page'})
  public pageVariable!: string

  public get destination() {
    if (!this.to) {
      return undefined
    }
    if (!this.trackPages) {
      return this.to
    }
    if (!this.list) {
      return this.to
    }
    const route = cloneDeep(this.to)
    if (this.list.currentPage > 1) {
      const query = route.query || {}
      query[this.pageVariable] = this.list.currentPage + ''
      route.query = query
    }
    return route
  }
}

export default toNative(AcTab)
</script>
