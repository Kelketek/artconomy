<template>
  <v-container>
    <ac-tab-nav label="View" :items="tabSpecs" class="table-dashboard-nav" />
    <router-view />
  </v-container>
</template>

<script setup lang="ts">
import AcTabNav from "@/components/navigation/AcTabNav.vue"
import { mdiReceipt, mdiShopping, mdiStorefront } from "@mdi/js"
import { listenForList } from "@/store/lists/hooks.ts"
import { useRoute, useRouter } from "vue-router"
import type { TabNavSpec } from "@/types/main"

const route = useRoute()
const router = useRouter()

const tabSpecs: TabNavSpec[] = [
  {
    value: { name: "TableProducts" },
    title: "Products",
    icon: mdiStorefront,
  },
  {
    value: { name: "TableOrders" },
    title: "Orders",
    icon: mdiShopping,
  },
  {
    value: { name: "TableInvoices" },
    title: "Invoices",
    icon: mdiReceipt,
  },
]

listenForList("table_products")
listenForList("table_orders")
listenForList("table_invoices")
if (route.name === "TableDashboard") {
  router.replace({ name: "TableProducts" })
}
</script>
