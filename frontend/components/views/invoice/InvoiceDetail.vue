<template>
  <ac-load-section :controller="invoice">
    <template v-slot:default>
      <v-container>
        <v-card>
          <v-card-text>
            <v-row>
              <v-col cols="2" class="text-left"><v-img src="/static/images/logo.svg" max-height="3rem" max-width="3rem"/></v-col>
              <v-col cols="7" class="text-left" align-self="center"><h1>Artconomy.com</h1></v-col>
              <v-col cols="3" class="text-right" align-self="center"><h2 class="text-uppercase">Invoice</h2></v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-simple-table>
                  <template v-slot:default>
                    <tr>
                      <td><strong>ID:</strong></td>
                      <td>{{invoice.x.id}}</td>
                    </tr>
                    <tr>
                      <td><strong>Created On:</strong></td>
                      <td>{{formatDateTime(invoice.x.created_on)}}</td>
                    </tr>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <ac-load-section :controller="lineItems">
                  <template v-slot:default>
                    <ac-line-item-listing :editable="editable" :edit-base="editable" :line-items="lineItems" :edit-extras="editable" />
                  </template>
                </ac-load-section>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import Viewer from '@/mixins/viewer'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import Invoice from '@/types/Invoice'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Formatting from '@/mixins/formatting'
import {ListController} from '@/store/lists/controller'
import LineItem from '@/types/LineItem'
import AcLineItemListing from '@/components/price_preview/AcLineItemListing.vue'
import {InvoiceStatus} from '@/types/InvoiceStatus'

@Component({
  components: {AcLineItemListing, AcLoadSection},
})
export default class InvoiceDetail extends mixins(Subjective, Viewer, Formatting) {
  @Prop({required: true})
  public invoiceId!: string

  public invoice = null as unknown as SingleController<Invoice>

  public lineItems = null as unknown as ListController<LineItem>

  public get editable() {
    return this.isStaff && this.invoice.x!.status === InvoiceStatus.OPEN
  }

  public created() {
    this.invoice = this.$getSingle(`invoice__${this.invoiceId}`, {endpoint: `/api/sales/v1/invoices/${this.invoiceId}/`})
    this.invoice.get()
    this.lineItems = this.$getList(`invoice__${this.invoiceId}__line_items`, {
      endpoint: `/api/sales/v1/invoices/${this.invoiceId}/line-items/`,
      paginated: false,
    })
    this.lineItems.firstRun()
  }
}
</script>
