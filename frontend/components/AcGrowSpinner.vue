<template>
  <v-col v-observe-visibility="grower">
    <ac-loading-spinner :min-height="minHeight" v-if="list.fetching"></ac-loading-spinner>
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

    @Watch('list.moreToLoad', {immediate: true})
    public updateMore(val: boolean) {
      if (val) {
        this.list.grower(this.visible)
      }
    }

    public grower(val: boolean) {
      this.visible = val
      this.list.grower(val)
    }
}
</script>
