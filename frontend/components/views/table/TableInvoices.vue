<template>
  <v-container class="pa-0" v-if="currentRoute">
    <v-row>
      <v-col cols="12" class="text-center py-8">
        <ac-form-container v-bind="invoiceForm.bind">
          <ac-form @submit.prevent="invoiceForm.submitThen(goToInvoice)">
            <v-btn color="green" block type="submit"><v-icon>receipt</v-icon>New invoice</v-btn>
          </ac-form>
        </ac-form-container>
      </v-col>
    </v-row>
    <ac-paginated :list="invoices" class="py-8">
      <template v-slot:default>
        <v-col cols="12" md="6" lg="4" offset-md="3" offset-lg="4">
          <v-toolbar>
            <v-toolbar-title>History</v-toolbar-title>
          </v-toolbar>
          <v-list>
            <v-list-item v-for="invoice in invoices.list" :key="invoice.x.id">
              <v-list-item-content>
                <v-list-item-title>
                  <ac-link :to="linkFor(invoice.x)">{{invoice.x.id}}</ac-link>
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{formatDateTime(invoice.x.created_on)}}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                {{invoice.x.total}}
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-container>
  <v-container class="pa-0" v-else>
    <v-toolbar class="table-invoice-toolbar">
      <v-toolbar-items>
        <v-btn @click="() => $router.go(-1)" color="secondary">
          <v-icon left>arrow_back</v-icon>
          Back
        </v-btn>
        <v-btn color="primary" @click="performPrint">
          <v-icon left>print</v-icon>
          Print
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <router-view />
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

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {ListController} from '@/store/lists/controller'
import Invoice from '@/types/Invoice'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {FormController} from '@/store/forms/form-controller'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import {SingleController} from '@/store/singles/controller'
import {NavSettings} from '@/types/NavSettings'
import {Prop} from 'vue-property-decorator'
import {initDrawerValue} from '@/lib/lib'

@Component({
  components: {AcLink, AcForm, AcFormContainer, AcPaginated},
})
export default class TableInvoices extends mixins(Viewer, Formatting) {
  invoices = null as unknown as ListController<Invoice>
  invoiceForm = null as unknown as FormController
  navSettings = null as unknown as SingleController<NavSettings>

  @Prop({default: initDrawerValue})
  public initialState!: null|boolean

  public get currentRoute() {
    return this.$route.name === 'TableInvoices'
  }

  public usernameFor(invoice: Invoice) {
    return (invoice.bill_to && invoice.bill_to.username) || this.viewer!.username
  }

  public goToInvoice(invoice: Invoice) {
    this.invoices.push(invoice)
    this.$router.push(this.linkFor(invoice))
  }

  public performPrint() {
    this.navSettings.patchers.drawer.model = false
    setTimeout(() => {
      window.print()
    }, 500)
  }

  public linkFor(invoice: Invoice) {
    return {name: 'TableInvoice', params: {username: this.usernameFor(invoice), invoiceId: invoice.id}}
  }

  public created() {
    let drawer: boolean | null
    if (this.$vuetify.breakpoint.mdAndDown) {
      // Never begin with the drawer open on a small screen.
      drawer = false
    } else {
      drawer = this.initialState
    }
    this.navSettings = this.$getSingle('navSettings', {
      endpoint: '#',
      x: {drawer},
    })
    this.navSettings = this.$getSingle('navSettings')
    this.invoiceForm = this.$getForm('new_invoice_button', {endpoint: '/api/sales/v1/create-anonymous-invoice/', fields: {}})
    this.invoices = this.$getList('table_invoices', {endpoint: '/api/sales/v1/recent-invoices/'})
    this.invoices.firstRun()
  }
}
</script>
