<template>
  <v-toolbar-items v-if="stats.x" variant="flat" class="ml-1">
    <v-btn icon variant="plain" v-if="stats" :to="{name: 'CurrentSales', params: {username}}">
      <span class="active-order-count">{{stats.x.active_orders}}</span>
      <v-badge :content="newCount" color="success" :model-value="!!newCount">
        <v-icon icon="mdi-invoice-text-outline" />
      </v-badge>
    </v-btn>
  </v-toolbar-items>
</template>

<script setup lang="ts">
import {useSingle} from '@/store/singles/hooks.ts'
import {flatten, getSalesStatsSchema} from '@/lib/lib.ts'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import CommissionStats from '@/types/CommissionStats.ts'
import {computed} from 'vue'

const props = defineProps<SubjectiveProps>()

const stats = useSingle<CommissionStats>(`stats__sales__${flatten(props.username)}`, getSalesStatsSchema(props.username))

stats.get()

const newCount = computed(() => {
  if (!stats.x) {
    return 0
  }
  return stats.x.new_orders
})
</script>
