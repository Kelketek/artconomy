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
                    <tr>
                      <td><strong>Status:</strong></td>
                      <td><ac-invoice-status :invoice="invoice.x" /></td>
                    </tr>
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <ac-load-section :controller="lineItems">
                  <template v-slot:default>
                    <ac-line-item-listing :editable="editable" :line-items="lineItems" :edit-extras="editable" />
                  </template>
                </ac-load-section>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6" lg="4" offset-md="4" class="text-center">
                <ac-form-container v-bind="stateChange.bind">
                  <v-row>
                    <v-col class="text-center" v-if="invoice.x.status === DRAFT">
                      <v-btn  color="primary" @click="() => statusEndpoint('finalize')">Finalize</v-btn>
                    </v-col>
                    <v-col class="text-center" v-if="invoice.x.status === OPEN">
                      <v-btn color="green" @click="() => showPayment = true">Pay</v-btn>
                    </v-col>
                    <v-col class="text-center" v-if="[DRAFT, OPEN].includes(invoice.x.status)">
                      <v-btn color="danger" @click="() => statusEndpoint('void')">Void</v-btn>
                    </v-col>
                  </v-row>
                </ac-form-container>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <ac-form-dialog
            v-model="showPayment" @submit.prevent="paymentSubmit"
            :large="true" v-bind="paymentForm.bind"
        >
          <v-row>
            <v-col class="text-center" cols="12" >Total Charge: <strong>${{totalCharge.toFixed(2)}}</strong></v-col>
            <v-col cols="12">
              <ac-load-section :controller="invoice">
                <template v-slot:default>
                  <ac-card-manager
                      ref="cardManager"
                      :payment="true"
                      :username="invoice.x.bill_to.username"
                      processor="stripe"
                      :cc-form="paymentForm"
                      :field-mode="true"
                      :show-save="false"
                      :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                      v-model="paymentForm.fields.card_id.model"
                      @paymentSent="() => showPayment = false"
                      v-if="!paymentForm.fields.cash.value"
                  />
                  <v-row>
                    <v-col>
                      <ac-bound-field
                          :field="paymentForm.fields.cash"
                          v-if="isStaff"
                          label="Cash transaction"
                          hint="Tick this box if the customer has handed you cash."
                          :persistent-hint="true"
                          field-type="ac-checkbox"
                      />
                    </v-col>
                  </v-row>
                </template>
              </ac-load-section>
            </v-col>
          </v-row>
        </ac-form-dialog>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import Viewer from '@/mixins/viewer'
import {Prop, Watch} from 'vue-property-decorator'
import {Big} from 'big.js'
import {SingleController} from '@/store/singles/controller'
import Invoice from '@/types/Invoice'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Formatting from '@/mixins/formatting'
import {ListController} from '@/store/lists/controller'
import LineItem from '@/types/LineItem'
import AcLineItemListing from '@/components/price_preview/AcLineItemListing.vue'
import {InvoiceStatus} from '@/types/InvoiceStatus'
import {FormController} from '@/store/forms/form-controller'
import AcInvoiceStatus from '@/components/AcInvoiceStatus.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin'
import {reckonLines} from '@/lib/lineItemFunctions'
import {baseCardSchema} from '@/lib/lib'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcBoundField from '@/components/fields/AcBoundField'

@Component({
  components: {
    AcBoundField,
    AcCardManager,
    AcFormDialog,
    AcFormContainer,
    AcInvoiceStatus,
    AcLineItemListing,
    AcLoadSection,
  },
})
export default class InvoiceDetail extends mixins(Subjective, Viewer, Formatting, StripeHostMixin) {
  @Prop({required: true})
  public invoiceId!: string

  public invoice = null as unknown as SingleController<Invoice>
  public lineItems = null as unknown as ListController<LineItem>
  public stateChange = null as unknown as FormController
  public showPayment = false

  DRAFT = InvoiceStatus.DRAFT
  OPEN = InvoiceStatus.OPEN

  public get editable() {
    return this.isStaff && this.invoice.x!.status === InvoiceStatus.DRAFT
  }

  public statusEndpoint(append: string) {
    this.stateChange.endpoint = `${this.url}${append}/`
    this.stateChange.submit()
  }

  get url() {
    return `/api/sales/v1/invoices/${this.invoiceId}/`
  }

  get totalCharge() {
    if (!this.lineItems || (this.lineItems.list.length === 0)) {
      return new Big('0.00')
    }
    return reckonLines(this.lineItems.list.map((item) => item.x as LineItem))
  }

  @Watch('totalCharge')
  public updateForLines(newVal: Big, oldVal: Big) {
    this.paymentForm.fields.amount.model = newVal.toString()
    if (newVal.eq(oldVal)) {
      return
    }
    this.updateIntent()
  }

  public get canUpdate() {
    if (this.paymentForm.fields.cash.value) {
      return false
    }
    const invoice = this.invoice && this.invoice.x
    if (!invoice) {
      return false
    }
    if (invoice.status !== InvoiceStatus.OPEN) {
      return false
    }
    return true
  }

  @Watch('invoice.x')
  public enableIntent(invoice: null | Invoice) {
    this.updateIntent()
    if (invoice && invoice.status !== InvoiceStatus.OPEN) {
      this.showPayment = false
    }
  }

  public paymentSubmit() {
    if (this.paymentForm.fields.cash.value) {
      this.paymentForm.submit()
    } else {
      const cardManager = this.$refs.cardManager as any
      cardManager.stripeSubmit()
    }
  }

  public get prefix() {
    return `invoice__${this.invoiceId}`
  }

  public created() {
    const schema = baseCardSchema(`${this.url}pay/`)
    schema.fields = {
      ...schema.fields,
      card_id: {value: null},
      service: {value: null},
      amount: {value: 0},
      remote_id: {value: ''},
      cash: {value: false},
      make_primary: {value: false},
      save_card: {value: false},
    }
    schema.reset = false
    this.paymentForm = this.$getForm(`${this.prefix}__payment`, schema)
    this.clientSecret = this.$getSingle(`${this.prefix}__clientSecret`, {endpoint: `${this.url}payment-intent/`})
    this.stateChange = this.$getForm(`${this.prefix}__stateChange`, {endpoint: this.url, fields: {}})
    this.invoice = this.$getSingle(`${this.prefix}`, {
      endpoint: this.url,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'Invoice',
        serializer: 'InvoiceSerializer',
      },
    })
    this.invoice.get()
    this.lineItems = this.$getList(`${this.prefix}__line_items`, {
      endpoint: `/api/sales/v1/invoices/${this.invoiceId}/line-items/`,
      paginated: false,
    })
    this.lineItems.firstRun()
  }
}
</script>
