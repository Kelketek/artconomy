<template>
  <v-container>
    <ac-tab-nav label="View" :items="tabSpecs" />
    <router-view />
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {TabNavSpec} from '@/types/TabNavSpec'
import AcTabNav from '@/components/navigation/AcTabNav.vue'

@Component({
  components: {AcTabNav, AcProductPreview, AcLink, AcAvatar, AcLoadSection}
})
export default class TableDashboard extends mixins(Viewer) {
  public tabSpecs: TabNavSpec[] = [
    {value: {name: 'TableProducts'}, text: 'Products', icon: 'storefront'},
    {value: {name: 'TableOrders'}, text: 'Orders', icon: 'shopping_bag'},
  ]

  created() {
    this.$listenForList('table_products')
    this.$listenForList('table_orders')
    if (this.$route.name === 'TableDashboard') {
      this.$router.replace({name: 'TableProducts'})
    }
  }
}
</script>
