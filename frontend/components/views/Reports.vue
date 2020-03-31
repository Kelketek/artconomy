<template>
  <v-container>
    <v-row>
      <v-col cols="12" lg="4">
        <v-subheader>Start Date</v-subheader>
        <v-date-picker v-model="startDate" label="Start Date"></v-date-picker>
        <v-subheader>End Date</v-subheader>
        <v-date-picker v-model="endDate" label="End Date"></v-date-picker>
      </v-col>
      <v-col cols="12" lg="7" offset-lg="1">
        <v-toolbar dense><v-toolbar-title>Current Holdings by Customer</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a href="/api/sales/v1/reports/customer-holdings/csv/" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Order report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/v1/reports/order-values/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Subscription Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/v1/reports/subscription-report/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Payout Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/v1/reports/payout-report/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar dense><v-toolbar-title>Dwolla Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/v1/reports/dwolla-report/csv/${rangeString}`" download>Download CSV</a></v-col>
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
    public startDate = ''
    public endDate = ''
    public get rangeKwargs() {
      const kwargs: {[key: string]: string} = {}
      if (this.startDate) {
        kwargs.start_date = this.startDate
      }
      if (this.endDate) {
        kwargs.end_date = this.endDate
      }
      return kwargs
    }
    public get rangeString() {
      const str = Object.keys(this.rangeKwargs).map(key => key + '=' + this.rangeKwargs[key]).join('&')
      if (str) {
        return `?${str}`
      }
      return ''
    }
    public created() {
      this.overview = this.$getSingle('overviewReport', {endpoint: '/api/sales/v1/reports/overview/'})
      this.overview.get()
    }
}
</script>

<style scoped>

</style>
