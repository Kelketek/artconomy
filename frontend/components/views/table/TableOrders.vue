<template>
  <ac-load-section :controller="orderList">
    <v-row
      v-for="[username, orders] of ordersByUser"
      :key="username"
    >
      <v-col cols="12">
        <v-toolbar
          :key="`${username}-header`"
          :dense="true"
          color="black"
        >
          <ac-avatar
            :username="username"
            :show-name="false"
            class="ml-3"
          />
          <v-toolbar-title class="ml-1">
            <ac-link :to="{name: 'AboutUser', params: {username}}">
              {{ username }}
            </ac-link>
          </v-toolbar-title>
        </v-toolbar>
      </v-col>
      <v-col
        v-for="order in orders"
        :key="order.id"
        cols="12"
        sm="3"
        md="4"
        lg="3"
        xl="2"
      >
        <ac-order-preview
          :order="order"
          :type="'sale'"
          :username="username"
        />
      </v-col>
    </v-row>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import {computed} from 'vue'
import {useList} from '@/store/lists/hooks.ts'
import type {Order} from '@/types/main'


const ordersByUser = computed(() => {
  const result = new Map()
  for (const order of orderList.list) {
    const username = order.x!.seller.username
    if (!result.has(username)) {
      result.set(username, [])
    }
    result.get(username).push(order)
  }
  return result
})

const orderList = useList<Order>('table_orders', {
  endpoint: '/api/sales/table/orders/',
  paginated: false,
})
orderList.firstRun()
</script>
