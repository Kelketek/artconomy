<template>
  <v-container>
    <v-row>
      <v-col cols="6" class="text-center">
        <div class="text-center">
          <span class="title" aria-hidden="true">Start Date</span>
        </div>
        <v-date-picker v-model="startDate" label="Start Date"></v-date-picker>
      </v-col>
      <v-col cols="6" class="text-center">
        <div class="text-center">
          <span class="title" aria-hidden="true">End Date</span>
        </div>
        <v-date-picker v-model="endDate" label="End Date"></v-date-picker>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
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
        <v-toolbar dense><v-toolbar-title>Unaffiliated Sales Report</v-toolbar-title></v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/v1/reports/unaffiliated-sales/csv/${rangeString}`" download>Download CSV</a></v-col>
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
import Component, {mixins} from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import OverviewReport from '@/types/OverviewReport'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import RangeReport from '@/components/views/reports/mixins/RangeReport'

@Component({
  components: {AcPaginated, AcLoadSection},
})
export default class Reports extends mixins(RangeReport) {
    public overview: SingleController<OverviewReport> = null as unknown as SingleController<OverviewReport>

    public created() {
      this.overview = this.$getSingle('overviewReport', {endpoint: '/api/sales/v1/reports/overview/'})
      this.overview.get()
    }
}
</script>

<style scoped>

</style>
