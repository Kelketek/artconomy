<template>
  <v-col v-observe-visibility="grower">
    <ac-loading-spinner :min-height="minHeight" v-if="list.fetching && list.currentPage > 1"/>
  </v-col>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
import AcLoadingSpinner from './wrappers/AcLoadingSpinner.vue'
import {ListController} from '@/store/lists/controller.ts'

@Component({
  components: {AcLoadingSpinner},
})
class AcGrowSpinner extends Vue {
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

  public grower(val: boolean) {
    this.visible = val
    this.list.grower(val)
  }
}

export default toNative(AcGrowSpinner)
</script>
