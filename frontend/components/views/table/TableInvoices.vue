<template>
  <v-container
    v-if="currentRoute"
    class="pa-0"
  >
    <v-row>
      <v-col
        cols="12"
        class="text-center py-8"
      >
        <ac-form-container v-bind="invoiceForm.bind">
          <ac-form @submit.prevent="invoiceForm.submitThen(goToInvoice)">
            <v-btn
              color="green"
              block
              type="submit"
              variant="flat"
            >
              <v-icon :icon="mdiReceiptText" />
              New invoice
            </v-btn>
          </ac-form>
        </ac-form-container>
      </v-col>
    </v-row>
    <ac-paginated
      :list="invoices"
      class="py-8"
    >
      <template #default>
        <v-col
          cols="12"
          md="6"
          lg="4"
          offset-md="3"
          offset-lg="4"
        >
          <v-toolbar>
            <v-toolbar-title>History</v-toolbar-title>
          </v-toolbar>
          <v-list>
            <v-list-item
              v-for="invoice in invoices.list"
              :key="invoice.x!.id"
            >
              <v-list-item-title>
                <ac-link :to="linkFor(invoice.x!)">
                  {{ invoice.x!.id }}
                </ac-link>
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDateTime(invoice.x!.created_on) }}
              </v-list-item-subtitle>
              <template #append>
                {{ invoice.x!.total }}
              </template>
            </v-list-item>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
  <v-container
    v-else
    class="pa-0"
  >
    <v-toolbar class="table-invoice-toolbar">
      <v-toolbar-items>
        <v-btn
          color="secondary"
          variant="flat"
          @click="() => router.go(-1)"
        >
          <v-icon
            left
            :icon="mdiArrowLeftThick"
          />
          Back
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="performPrint"
        >
          <v-icon
            left
            :icon="mdiPrinter"
          />
          Print
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <router-view />
  </v-container>
</template>

<script setup lang="ts">
import {useViewer} from '@/mixins/viewer.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {initDrawerValue} from '@/lib/lib.ts'
import {mdiArrowLeftThick, mdiPrinter, mdiReceiptText} from '@mdi/js'
import {useRoute, useRouter} from 'vue-router'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import type {Invoice, NavSettings} from '@/types/main'

const props = withDefaults(defineProps<{initialState?: null|boolean}>(), {initialState: initDrawerValue()})

const route = useRoute()
const router = useRouter()
const display = useDisplay()
const {viewer} = useViewer()

const currentRoute = computed(() => route.name === 'TableInvoices')

const usernameFor = (invoice: Invoice) => {
  return (invoice.bill_to && invoice.bill_to.username) || viewer.value!.username
}

const goToInvoice = (invoice: Invoice) => {
  invoices.push(invoice)
  router.push(linkFor(invoice))
}

const linkFor = (invoice: Invoice) => {
  return {
    name: 'TableInvoice',
    params: {
      username: usernameFor(invoice),
      invoiceId: invoice.id,
    },
  }
}

const performPrint = () => {
  navSettings.patchers.drawer.model = false
  setTimeout(() => {
    window.print()
  }, 500)
}

let drawer: boolean | null
if (display.mdAndDown.value) {
  // Never begin with the drawer open on a small screen.
  drawer = false
} else {
  drawer = props.initialState
}

const navSettings = useSingle<NavSettings>('navSettings', {
  endpoint: '#',
  x: {drawer},
})
const invoiceForm = useForm('new_invoice_button', {
  endpoint: '/api/sales/create-anonymous-invoice/',
  fields: {},
})
const invoices = useList<Invoice>('table_invoices', {endpoint: '/api/sales/table-invoices/'})
invoices.firstRun()
</script>

<style>
@media print {
  .table-invoice-toolbar {
    display: none;
  }

  .table-dashboard-nav {
    display: none;
  }

  .main-navigation {
    display: none;
  }
}
</style>
