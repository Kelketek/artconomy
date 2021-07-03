<template>
  <v-tab :to="destination" :value="value">
    <v-icon left v-if="icon">{{icon}}</v-icon>
    <slot></slot>
    <span v-if="count">&nbsp;({{count}})</span>
  </v-tab>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {ListController} from '@/store/lists/controller'
import {Prop} from 'vue-property-decorator'
import cloneDeep from 'lodash/cloneDeep'
import {Route} from 'vue-router'
import {TabSpec} from '@/types/TabSpec'

  @Component
export default class AcTab extends Vue {
    @Prop()
    public icon!: string

    @Prop()
    public list!: ListController<any>|null

    @Prop()
    public count!: number

    @Prop()
    public to!: Route

    @Prop({required: false})
    public value!: TabSpec

    @Prop({default: true})
    public trackPages!: boolean

    @Prop({default: 'page'})
    public pageVariable!: string

    public get destination() {
      if (!this.to) {
        return
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
</script>
