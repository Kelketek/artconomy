<template>
  <v-container class="pa-0" fluid>
    <v-row no-gutters>
      <v-col class="shrink text-center" cols="12">
        <v-pagination :length="list.totalPages" v-model="list.currentPage" v-if="list.totalPages > 1 && showPagination" :class="{prerendering}" />
      </v-col>
      <v-col cols="12">
        <ac-load-section :controller="list" class="load-section" :force-render="list.grow && list.list.length" :load-on-grow="false">
          <template v-slot:default>
            <v-row no-gutters v-if="list.list.length">
              <slot>
                <v-col v-for="item in list.list" :key="item.key">{{item.x}}</v-col>
              </slot>
            </v-row>
            <v-row no-gutters  v-else>
              <slot name="empty">
                <v-col class="text-center" >
                  Nothing to see here.
                </v-col>
              </slot>
            </v-row>
          </template>
          <template slot="failure">
            <slot name="failure"/>
          </template>
        </ac-load-section>
      </v-col>
      <v-col class="text-center" cols="12" v-if="list.grow">
        <ac-grow-spinner :list="list" />
      </v-col>
      <v-col class="shrink text-center" cols="12">
        <v-pagination :length="list.totalPages" v-model="list.currentPage" v-if="list.totalPages > 1 && showPagination" :class="{prerendering}" />
      </v-col>
    </v-row>
  </v-container>
</template>

<style>
  .v-pagination.prerendering .v-pagination__item {
    display: none;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import {Prop, Watch} from 'vue-property-decorator'
import ErrorHandling from '@/mixins/ErrorHandling'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'

  @Component({
    components: {AcGrowSpinner, AcLoadSection},
  })
export default class AcPaginated extends mixins(ErrorHandling) {
    @Prop({default: true})
    public autoRun!: boolean
    @Prop({default: false})
    public trackPages!: boolean
    @Prop({default: 'page'})
    public pageVariable!: string
    @Prop({required: true})
    public list!: ListController<any>
    @Prop({default: () => []})
    public okStatuses!: number[]
    @Prop({default: true})
    public showPagination!: boolean
    public prerendering = window.PRERENDERING || 0

    @Watch('list.currentPage')
    public updateRoute(val: number|undefined) {
      // istanbul ignore if
      if (!val) {
        return
      }
      if (!this.trackPages) {
        return
      }
      const route = {...this.$route.query}
      route[this.pageVariable] = val + ''
      this.$router.replace({query: route})
    }
    public created() {
      if (this.trackPages) {
        if (this.$route.query[this.pageVariable]) {
          this.list.currentPage = parseInt(this.$route.query[this.pageVariable] + '', 10)
        }
      }
      if (this.autoRun) {
        this.list.firstRun().catch(this.statusOk(...this.okStatuses))
      }
    }
}
</script>
