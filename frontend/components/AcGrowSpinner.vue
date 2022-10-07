<template>
  <v-col v-observe-visibility="{callback: grower, intersection: {rootMargin}}">
    <ac-loading-spinner :min-height="minHeight" v-if="list.fetching && list.currentPage > 1" />
  </v-col>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import AcLoadingSpinner from './wrappers/AcLoadingSpinner.vue'
import {ListController} from '@/store/lists/controller'
  @Component({
    components: {AcLoadingSpinner},
  })
export default class AcGrowSpinner extends Vue {
    @Prop({default: '3rem'})
    public minHeight!: string

    @Prop({required: true})
    public list!: ListController<any>

    public visible = false

    @Watch('list.fetching', {immediate: true})
    public updateFetching(val: boolean) {
      if (!val) {
        this.grower(this.visible)
      }
    }

    @Watch('list.moreAvailable', {immediate: true})
    public updateMore(val: boolean) {
      if (val) {
        this.list.grower(this.visible)
      }
    }

    public get rootMargin() {
      return `0px 0px ${window.innerHeight * 1.5}px 0px`
    }

    public grower(val: boolean) {
      this.visible = val
      this.list.grower(val)
    }
}
</script>
