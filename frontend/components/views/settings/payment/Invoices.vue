<template>
  <v-container class="pa-0" v-if="currentRoute">
    <ac-paginated :list="invoices" class="py-8">
      <template v-slot:default>
        <v-col cols="12" md="8" offset-md="2">
          <v-list>
            <template v-for="invoice, invoiceIndex in invoices.list" :key="invoice.x!.id">
              <v-list-item class="my-2">
                <v-list-item-title>
                  <ac-link :to="{name: 'Invoice', params: {username, invoiceId: invoice.x!.id}}">{{invoice.x!.id}}
                  </ac-link>
                  ({{INVOICE_TYPES[invoice.x!.type]}})
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{formatDateTime(invoice.x!.created_on)}}
                  <span v-for="ref, index in invoice.x!.targets" :key="index">
                  <ac-link :to="ref.link"><span v-if="ref.display_name">{{ref.display_name}}</span><span v-else>{{ref.model}} #{{ref.id}}</span></ac-link><span
                      v-if="index !== (invoice.x!.targets.length - 1)">,</span>
                </span>
                </v-list-item-subtitle>
                <template v-slot:append>
                  {{invoice.x!.total}}
                  <ac-invoice-status :invoice="invoice.x!" class="ml-2"/>
                </template>
              </v-list-item>
              <v-divider v-if="invoiceIndex !== (invoices.list.length - 1)"/>
            </template>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
  <v-container class="pa-0" v-else>
    <v-toolbar class="invoice-toolbar">
      <v-toolbar-items>
        <v-btn @click="goBack" color="secondary" variant="flat">
          <v-icon left :icon="mdiArrowLeftBold"/>
          Back
        </v-btn>
        <v-btn color="primary" variant="flat" @click="performPrint">
          <v-icon left :icon="mdiPrinter"/>
          Print
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <router-view/>
  </v-container>
</template>

<style>
@media print {
  .invoice-toolbar, .main-navigation, .invoice-actions, .settings-nav-toolbar, .transactions-list {
    display: none;
  }
}
</style>

<script setup lang="ts">
import Invoice from '@/types/Invoice.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {initDrawerValue, INVOICE_TYPES} from '@/lib/lib.ts'
import AcInvoiceStatus from '@/components/AcInvoiceStatus.vue'
import {mdiArrowLeftBold, mdiPrinter} from '@mdi/js'
import {useDisplay} from 'vuetify'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useRoute, useRouter} from 'vue-router'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import {computed} from 'vue'

const props = withDefaults(defineProps<{initialState: boolean|null} & SubjectiveProps>(), {initialState: initDrawerValue()})

const display = useDisplay()
const router = useRouter()
const route = useRoute()

let drawer: boolean | null
if (display.mdAndDown.value) {
  // Never begin with the drawer open on a small screen.
  drawer = false
} else {
  drawer = props.initialState
}
const navSettings = useSingle('navSettings', {
  endpoint: '#',
  x: {drawer},
})
const invoices = useList<Invoice>(`${props.username}__invoices`, {endpoint: `/api/sales/account/${props.username}/invoices/`})
invoices.firstRun()

const performPrint = () => {
  navSettings.patchers.drawer.model = false
  setTimeout(() => {
    window.print()
  }, 500)
}

const goBack = () => {
  router.replace({
    name: 'Invoices',
    params: {username: props.username},
  })
}

const currentRoute = computed(() => {
  return route.name === 'Invoices'
})
</script>
