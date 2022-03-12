<template>
  <v-container class="pa-0">
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
                  <ac-link :to="{name: 'InvoiceDetail', params: {username: invoice.x.bill_to.username, invoiceId: invoice.x.id}}">{{invoice.x.id}}</ac-link>
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
</template>

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

@Component({
  components: {AcLink, AcForm, AcFormContainer, AcPaginated},
})
export default class TableInvoices extends mixins(Viewer, Formatting) {
  invoices = null as unknown as ListController<Invoice>
  invoiceForm = null as unknown as FormController

  public goToInvoice(invoice: Invoice) {
    this.$router.push({name: 'InvoiceDetail', params: {username: invoice.bill_to.username, invoiceId: invoice.id}})
  }

  public created() {
    this.invoiceForm = this.$getForm('new_invoice_button', {endpoint: '/api/sales/v1/create-anonymous-invoice/', fields: {}})
    this.invoices = this.$getList('recent_invoices', {endpoint: '/api/sales/v1/recent-invoices/'})
    this.invoices.firstRun()
  }
}
</script>
