<template>
  <v-container>
    <ac-tab-nav label="View" :items="tabSpecs" class="table-dashboard-nav"/>
    <router-view/>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {TabNavSpec} from '@/types/TabNavSpec.ts'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {mdiReceipt, mdiShopping, mdiStorefront} from '@mdi/js'

@Component({
  components: {
    AcTabNav,
    AcProductPreview,
    AcLink,
    AcAvatar,
    AcLoadSection,
  },
})
class TableDashboard extends mixins(Viewer) {
  public tabSpecs: TabNavSpec[] = [
    {
      value: {name: 'TableProducts'},
      title: 'Products',
      icon: mdiStorefront,
    },
    {
      value: {name: 'TableOrders'},
      title: 'Orders',
      icon: mdiShopping,
    },
    {
      value: {name: 'TableInvoices'},
      title: 'Invoices',
      icon: mdiReceipt,
    },
  ]

  created() {
    this.$listenForList('table_products')
    this.$listenForList('table_orders')
    this.$listenForList('table_invoices')
    if (this.$route.name === 'TableDashboard') {
      this.$router.replace({name: 'TableProducts'})
    }
  }
}

export default toNative(TableDashboard)
</script>
