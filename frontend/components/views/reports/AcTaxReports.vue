<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Financial Reports</v-card-title>
          <v-card-text>
            On this page you will find financial reporting tools. These tools may become more sophisticated with time.
            For now, they allow you to download important information for tax purposes.
          </v-card-text>
        </v-card>
      </v-col>
      <v-col
        cols="6"
        class="text-center"
      >
        <div class="text-center">
          <span
            class="title"
            aria-hidden="true"
          >Start Date</span>
        </div>
        <v-date-picker
          v-model="startDate"
          label="Start Date"
        />
      </v-col>
      <v-col
        cols="6"
        class="text-center"
      >
        <div class="text-center">
          <span
            class="title"
            aria-hidden="true"
          >End Date</span>
        </div>
        <v-date-picker
          v-model="endDate"
          label="End Date"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-row no-gutters>
          <v-col class="text-center">
            <v-btn
              color="primary"
              :href="`/api/sales/account/${username}/reports/payout/${rangeString}`"
              variant="flat"
              download
            >
              Download Payout Report CSV
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {useRangeReport} from '@/components/views/reports/mixins/RangeReport.ts'

import type {SubjectiveProps} from '@/types/main'
defineProps<SubjectiveProps>()
const {startDate, endDate, rangeString} = useRangeReport()
</script>
