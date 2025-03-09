<template>
  <v-container class="pa-0" v-if="currentRoute">
    <v-row>
      <v-col cols="12" class="text-center py-8">
        <v-btn color="green" block type="submit" variant="flat"  @click="showNewInvoice = true">
          <v-icon :icon="mdiReceiptText"/>
          New invoice
        </v-btn>
      </v-col>
    </v-row>
    <ac-form-dialog v-model="showNewInvoice" v-bind="invoiceForm.bind" @submit.prevent="invoiceForm.submitThen(goToInvoice)">
      <v-row>
        <v-col cols="12" md="6" offset-md="3">
          <ac-bound-field
              :field="invoiceForm.fields.issued_by_id" field-type="ac-user-select"
              :multiple="false"
              label="User we're paying"
          />
        </v-col>
      </v-row>
    </ac-form-dialog>
    <ac-paginated :list="invoices" class="py-8">
      <template v-slot:default>
        <v-col cols="12" md="6" lg="4" offset-md="3" offset-lg="4">
          <v-toolbar>
            <v-toolbar-title>History</v-toolbar-title>
          </v-toolbar>
          <v-list>
            <v-list-item v-for="invoice in invoices.list" :key="invoice.x!.id">
              <v-list-item-title>
                <ac-link :to="linkFor(invoice.x!)">{{ invoice.x!.id }} to {{ invoice.x!.issued_by?.username}}</ac-link>
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDateTime(invoice.x!.created_on) }}
              </v-list-item-subtitle>
              <template v-slot:append>
                {{ invoice.x!.total }}
              </template>
            </v-list-item>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
  <v-container class="pa-0" v-else>
    <v-toolbar class="table-invoice-toolbar">
      <v-toolbar-items>
        <v-btn @click="() => router.go(-1)" color="secondary" variant="flat">
          <v-icon left :icon="mdiArrowLeftThick"/>
          Back
        </v-btn>
        <v-btn color="primary" @click="performPrint" variant="flat">
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

<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {initDrawerValue} from '@/lib/lib.ts'
import {mdiArrowLeftThick, mdiPrinter, mdiReceiptText} from '@mdi/js'
import {useRoute, useRouter} from 'vue-router'
import {computed, ref} from 'vue'
import {useDisplay} from 'vuetify'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import type {Invoice, NavSettings} from '@/types/main'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'

const props = withDefaults(defineProps<{initialState?: null|boolean}>(), {initialState: initDrawerValue()})

const route = useRoute()
const router = useRouter()
const display = useDisplay()

const currentRoute = computed(() => route.name === 'VendorInvoices')

const showNewInvoice = ref(false)

const goToInvoice = (invoice: Invoice) => {
  invoices.push(invoice)
  router.push(linkFor(invoice))
}

const linkFor = (invoice: Invoice) => {
  return {
    name: 'VendorInvoice',
    params: {
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
  endpoint: '/api/sales/create-vendor-invoice/',
  fields: {issued_by_id: {value: null}},
})
const invoices = useList<Invoice>('vendor_invoices', {endpoint: '/api/sales/vendor-invoices/'})
invoices.firstRun()
</script>
