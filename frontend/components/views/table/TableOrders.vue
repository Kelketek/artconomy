<template>
  <ac-load-section :controller="orderList">
    <v-row v-for="[username, orders] of ordersByUser" :key="username">
      <v-col cols="12">
        <v-toolbar :dense="true" color="black" :key="`${username}-header`">
          <ac-avatar :username="username" :show-name="false" class="ml-3"/>
          <v-toolbar-title class="ml-1">
            <ac-link :to="{name: 'AboutUser', params: {username}}">{{ username }}</ac-link>
          </v-toolbar-title>
        </v-toolbar>
      </v-col>
      <v-col cols="12" sm="3" md="4" lg="3" xl="2" v-for="order in orders" :key="order.id">
        <ac-order-preview :order="order" :type="'sale'" :username="username"/>
      </v-col>
    </v-row>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcProductPreview from '@/components/AcProductPreview.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Order from '@/types/Order.ts'
import AcOrderPreview from '@/components/AcOrderPreview.vue'

@Component({
  components: {
    AcOrderPreview,
    AcProductPreview,
    AcLink,
    AcAvatar,
    AcLoadSection,
  },
})
class TableOrders extends mixins(Viewer) {
  public orderList = null as unknown as ListController<Order>

  public get ordersByUser() {
    const result = new Map()
    for (const order of this.orderList.list) {
      const username = order.x!.seller.username
      if (!result.has(username)) {
        result.set(username, [])
      }
      result.get(username).push(order)
    }
    return result
  }

  public created() {
    this.orderList = this.$getList('table_orders', {
      endpoint: '/api/sales/table/orders/',
      paginated: false,
    })
    this.orderList.firstRun()
  }
}

export default toNative(TableOrders)
</script>
