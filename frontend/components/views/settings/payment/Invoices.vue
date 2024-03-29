<template>
  <v-container class="pa-0" v-if="currentRoute">
    <ac-paginated :list="invoices" class="py-8">
      <template v-slot:default>
        <v-col cols="12" md="8" offset-md="2">
          <v-list>
            <v-list-item v-for="invoice in invoices.list" :key="invoice.x!.id">
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
                <ac-invoice-status :invoice="invoice.x"/>
              </template>
            </v-list-item>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
  <v-container class="pa-0" v-else>
    <v-toolbar class="invoice-toolbar">
      <v-toolbar-items>
        <v-btn @click="goBack" color="secondary">
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

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {ListController} from '@/store/lists/controller.ts'
import Invoice from '@/types/Invoice.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {NavSettings} from '@/types/NavSettings.ts'
import {initDrawerValue, INVOICE_TYPES} from '@/lib/lib.ts'
import AcInvoiceStatus from '@/components/AcInvoiceStatus.vue'
import {mdiArrowLeftBold, mdiPrinter} from '@mdi/js'

@Component({
  components: {
    AcInvoiceStatus,
    AcLink,
    AcPaginated,
  },
})
class Invoices extends mixins(Subjective, Formatting) {
  public invoices = null as unknown as ListController<Invoice>
  public navSettings = null as unknown as SingleController<NavSettings>
  public INVOICE_TYPES = INVOICE_TYPES
  public mdiArrowLeftBold = mdiArrowLeftBold
  public mdiPrinter = mdiPrinter

  @Prop({default: initDrawerValue})
  public initialState!: null | boolean

  public get currentRoute() {
    return this.$route.name === 'Invoices'
  }

  public goBack() {
    this.$router.replace({
      name: 'Invoices',
      params: {username: this.username},
    })
  }

  public performPrint() {
    this.navSettings.patchers.drawer.model = false
    setTimeout(() => {
      window.print()
    }, 500)
  }

  public created() {
    let drawer: boolean | null
    if (this.$vuetify.display.mdAndDown) {
      // Never begin with the drawer open on a small screen.
      drawer = false
    } else {
      drawer = this.initialState
    }
    this.navSettings = this.$getSingle('navSettings', {
      endpoint: '#',
      x: {drawer},
    })
    this.invoices = this.$getList(`${this.username}__invoices`, {endpoint: `/api/sales/account/${this.username}/invoices/`})
    this.invoices.firstRun()
  }
}

export default toNative(Invoices)
</script>
