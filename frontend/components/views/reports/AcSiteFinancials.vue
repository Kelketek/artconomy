<template>
  <v-container>
    <v-row>
      <v-col cols="6" class="text-center">
        <div class="text-center">
          <span class="title" aria-hidden="true">Start Date</span>
        </div>
        <v-date-picker :model-value="startDate" label="Start Date"></v-date-picker>
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
        <v-toolbar density="compact">
          <v-toolbar-title>Current Holdings by Customer</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/customer-holdings/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Order report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/order-values/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Subscription Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/subscription-report/csv/${rangeString}`" download>Download CSV</a>
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Payout Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/payout-report/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Unaffiliated Sales Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/unaffiliated-sales/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Tip Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col><a :href="`/api/sales/reports/tip-report/csv/${rangeString}`" download>Download CSV</a></v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import OverviewReport from '@/types/OverviewReport.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import RangeReport from '@/components/views/reports/mixins/RangeReport.ts'

@Component({
  components: {
    AcPaginated,
    AcLoadSection,
  },
})
class Reports extends mixins(RangeReport) {
  public overview: SingleController<OverviewReport> = null as unknown as SingleController<OverviewReport>
}

export default toNative(Reports)
</script>

<style scoped>

</style>
