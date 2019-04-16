<template>
  <v-container class="pa-0" fluid>
    <v-layout column class="text-xs-center">
      <v-flex shrink text-xs-center>
        <v-pagination :length="list.totalPages" v-model="list.currentPage" v-if="list.totalPages > 1"></v-pagination>
      </v-flex>
      <v-flex>
        <ac-load-section :controller="list" class="load-section">
          <template v-slot:default>
            <v-layout row wrap v-if="list.list.length">
              <slot>
                <v-flex v-for="item in list.list" :key="item.key">{{item.x}}</v-flex>
              </slot>
            </v-layout>
            <v-layout row v-else>
              <slot name="empty">
                <v-flex text-xs-center>
                  Nothing to see here.
                </v-flex>
              </slot>
            </v-layout>
          </template>
        </ac-load-section>
      </v-flex>
      <v-flex shrink text-xs-center>
        <v-pagination :length="list.totalPages" v-model="list.currentPage" v-if="list.totalPages > 1"></v-pagination>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import {Prop, Watch} from 'vue-property-decorator'

  @Component({
    components: {AcLoadSection},
  })
export default class AcPaginated extends Vue {
    @Prop({default: true})
    public autoRun!: boolean
    @Prop({default: false})
    public trackPages!: boolean
    @Prop({default: 'page'})
    public pageVariable!: string
    @Prop({required: true})
    public list!: ListController<any>

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
        this.list.firstRun().then()
      }
    }
}
</script>
