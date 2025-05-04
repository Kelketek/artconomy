<template>
  <v-container>
    <v-row>
      <v-col cols="6" class="text-center">
        <div class="text-center">
          <span class="title" aria-hidden="true">Start Date</span>
        </div>
        <v-date-picker v-model="startDate" label="Start Date" />
      </v-col>
      <v-col cols="6" class="text-center">
        <div class="text-center">
          <span class="title" aria-hidden="true">End Date</span>
        </div>
        <v-date-picker v-model="endDate" label="End Date" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-toolbar density="compact">
          <v-toolbar-title>Current Holdings by Customer</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/customer-holdings/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Reconciliation Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/reconciliation-report/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Journal Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/journal-report/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Order report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/order-values/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Subscription Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/subscription-report/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Payout Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/payout-report/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Unaffiliated Sales Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/unaffiliated-sales/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
        <v-toolbar density="compact">
          <v-toolbar-title>Tip Report</v-toolbar-title>
        </v-toolbar>
        <v-row no-gutters>
          <v-col>
            <a
              :href="`/api/sales/reports/tip-report/csv/${rangeString}`"
              download
              >Download CSV</a
            >
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { useRangeReport } from "@/components/views/reports/mixins/RangeReport.ts"
const { startDate, endDate, rangeString } = useRangeReport()
</script>
