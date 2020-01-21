<template>
  <v-container>
    <v-row>
      <v-col cols="12" lg="4">
        <v-toolbar dense><v-toolbar-title>Overview</v-toolbar-title></v-toolbar>
        <ac-load-section :controller="overview">
          <v-data-table :items="overviewItems" :headers="overviewHeaders" hide-default-footer hide-default-header>
            <template v-slot:item.label="{ item }">
              <strong>{{item.label}}</strong>
            </template>
            <template v-slot:item.value="{ item }">
              ${{item.value}}
            </template>
          </v-data-table>
        </ac-load-section>
      </v-col>
      <v-col cols="12" lg="7" offset-lg="1">
        <v-toolbar dense><v-toolbar-title>Holdings by Customer</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/customer-holdings/csv/" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Order report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/order-values/csv/" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Subscription Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/subscription-report/csv/" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Payout Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/payout-report/csv/" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Dwolla Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/dwolla-report/csv/" download>Download CSV</a></v-col>
        </v-row>
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
import {axiosCatch} from '@/store/forms/field-controller'
import {artCall} from '@/lib/lib'
import moment from 'moment-timezone'
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
    public overviewHeaders = [{text: 'Label', value: 'label'}, {text: 'Value', value: 'value'}]
    public get overviewItems() {
      if (!this.overview.x) {
        return []
      }
      return [
        {label: 'Unqualified earnings', value: this.overview.x.unprocessed},
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
      this.holdings.currentPage = obj.page
    }
    public downloadHoldings() {
      artCall({
        url: this.holdings.endpoint, method: 'get', responseType: 'blob', headers: {Accept: 'text/csv'}},
      ).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `holdings-${moment.now()}.csv`)
        link.click()
      })
    }
    public created() {
      this.overview = this.$getSingle('overviewReport', {endpoint: '/api/sales/v1/reports/overview/'})
      this.overview.get()
    }
}
</script>

<style scoped>

</style>
