<template>
  <v-container>
    <v-row no-gutters  >
      <v-col cols="12" lg="4">
        <v-toolbar dense><v-toolbar-title>Overview</v-toolbar-title></v-toolbar>
        <ac-load-section :controller="overview">
          <v-data-table :items="overviewItems" :hide-actions="true" :hide-headers="true">
            <template v-slot:items="props">
              <td><strong>{{props.item.label}}</strong></td>
              <td>${{props.item.value}}</td>
            </template>
          </v-data-table>
        </ac-load-section>
      </v-col>
      <v-col cols="12" lg="7" offset-lg="1">
        <v-toolbar dense><v-toolbar-title>By Customer</v-toolbar-title></v-toolbar>
        <ac-paginated :list="holdings">
          <v-col>
            <v-data-table :items="holdingsItems" :headers="holdingsHeaders" :hide-actions="true" >
              <template v-slot:items="props">
                <td class="text-left"><strong>{{props.item.id}}</strong></td>
                <td class="text-left"><strong>{{props.item.username}}</strong></td>
                <td class="text-center">${{props.item.escrow}}</td>
                <td class="text-center">${{props.item.holdings}}</td>
              </template>
            </v-data-table>
          </v-col>
        </ac-paginated>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import OverviewReport from '@/types/OverviewReport'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import CustomerHolding from '@/types/CustomerHolding'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
  @Component({
    components: {AcPaginated, AcLoadSection},
  })
export default class App extends Vue {
    public overview: SingleController<OverviewReport> = null as unknown as SingleController<OverviewReport>
    public holdings: ListController<CustomerHolding> = null as unknown as ListController<CustomerHolding>
    public holdingsHeaders = [{
      text: 'ID',
      value: 'id',
      sortable: false,
      align: 'left',
    }, {
      text: 'Username',
      value: 'username',
      sortable: false,
      align: 'left',
    }, {
      text: 'Escrow',
      value: 'escrow',
      sortable: false,
      align: 'center',
    }, {
      text: 'Holdings',
      value: 'holdings',
      sortable: false,
      align: 'center',
    }]
    public get overviewItems() {
      if (!this.overview.x) {
        return []
      }
      return [
        {label: 'Cash available for withdraw', value: this.overview.x.earned},
        {label: 'Unprocessed earnings, needs card processor import', value: this.overview.x.unprocessed},
        {label: 'Reserve (may be given as Landscape bonus)', value: this.overview.x.reserve},
        {label: 'Held in escrow', value: this.overview.x.escrow},
        {label: 'Customer holdings awaiting withdraw', value: this.overview.x.holdings},
      ]
    }
    public get holdingsItems() {
      return this.holdings.list.map((x) => x.x)
    }
    public get holdingsPagination() {
      return {
        page: this.holdings.currentPage,
        rowsPerPage: this.holdings.pageSize,
        totalItems: this.holdings.count,
        sortBy: 'id',
        descending: false,
      }
    }
    public set holdingsPagination(obj: any) {
      console.log('I ran!', obj, this.holdings.pageSize)
      this.holdings.currentPage = obj.page
    }
    public created() {
      this.overview = this.$getSingle('overviewReport', {endpoint: '/api/sales/v1/reports/overview/'})
      this.overview.get()
      this.holdings = this.$getList('customerHoldings', {endpoint: '/api/sales/v1/reports/customer_holdings/'})
      this.holdings.firstRun()
    }
}
</script>

<style scoped>

</style>
