<template>
  <ac-load-section :controller="invoice">
    <template v-slot:default>
      <v-container v-if="invoice.x">
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-text>
                <v-row>
                  <v-col cols="2" class="text-left">
                    <v-img :src="logo" max-height="3rem" max-width="3rem" alt="Artconomy.com"/>
                  </v-col>
                  <v-col cols="7" class="text-left" align-self="center"><h1>Artconomy.com</h1></v-col>
                  <v-col cols="3" class="text-right" align-self="center"><h2 class="text-uppercase">Invoice</h2></v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" sm="6">
                    <v-simple-table>
                      <template v-slot:default>
                        <tr>
                          <td><strong>ID:</strong></td>
                          <td>{{ invoice.x.id }}</td>
                        </tr>
                        <tr>
                          <td><strong>Created On:</strong></td>
                          <td>{{ formatDateTime(invoice.x.created_on) }}</td>
                        </tr>
                        <tr>
                          <td><strong>Status:</strong></td>
                          <td>
                            <ac-invoice-status :invoice="invoice.x"/>
                          </td>
                        </tr>
                      </template>
                    </v-simple-table>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-simple-table>
                      <template v-slot:default>
                        <tr>
                          <td><strong>Type:</strong></td>
                          <td>{{ INVOICE_TYPES[invoice.x.type] }}</td>
                        </tr>
                        <tr>
                          <td><strong>Targets:</strong></td>
                          <td>
                        <span v-for="ref, index in invoice.x.targets" :key="index">
                          <ac-link :to="ref.link"><span v-if="ref.display_name">{{ ref.display_name }}</span><span
                              v-else>{{ ref.model }} #{{ ref.id }}</span></ac-link><span
                            v-if="index !== (invoice.x.targets.length - 1)">,</span>
                        </span>
                          </td>
                        </tr>
                        <tr>
                          <td><strong>Issued by:</strong></td>
                          <td>
                            <ac-link v-if="invoice.x.issued_by" :to="profileLink(invoice.x.issued_by)">
                              {{ invoice.x.issued_by.username }}
                            </ac-link>
                            <span v-else>Artconomy</span>
                          </td>
                        </tr>
                      </template>
                    </v-simple-table>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col>
                    <ac-load-section :controller="lineItems">
                      <template v-slot:default>
                        <ac-line-item-listing :editable="editable" :line-items="lineItems" :edit-extras="editable"/>
                      </template>
                    </ac-load-section>
                  </v-col>
                </v-row>
                <v-row class="invoice-actions">
                  <v-col cols="12" md="6" lg="4" offset-md="4" class="text-center">
                    <ac-form-container v-bind="stateChange.bind">
                      <v-row>
                        <v-col class="text-center" v-if="isStaff && (invoice.x.status === DRAFT)">
                          <v-btn color="primary" variant="flat" @click="() => statusEndpoint('finalize')">Finalize</v-btn>
                        </v-col>
                        <v-col class="text-center" v-if="invoice.x.status === OPEN">
                          <v-btn color="green" variant="flat" @click="() => showPayment = true">Pay</v-btn>
                        </v-col>
                        <v-col class="text-center" v-if="isStaff && ([DRAFT, OPEN].includes(invoice.x.status))">
                          <v-btn color="danger" variant="flat" @click="() => statusEndpoint('void')">Void</v-btn>
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
                <v-col class="text-center" cols="12">Total Charge: <strong>${{ totalCharge.toFixed(2) }}</strong>
                </v-col>
                <v-col cols="12">
                  <ac-load-section :controller="invoice">
                    <template v-slot:default>
                      <v-tabs v-model="cardTabs" class="mb-2" fixed-tabs v-if="isStaff">
                        <v-tab>Manual Entry</v-tab>
                        <v-tab>Terminal</v-tab>
                        <v-tab>Cash</v-tab>
                      </v-tabs>
                      <v-window v-model="cardTabs">
                        <v-window-item>
                          <v-card-text>
                            <v-row>
                              <v-col cols="12">
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
                              </v-col>
                            </v-row>
                            <v-col class="text-center" cols="12">
                              <p>Use of Artconomy is subject to the
                                <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
                                .<br/>
                                Commission orders are subject to the
                                <router-link :to="{name: 'CommissionAgreement'}">Commission Agreement</router-link>
                                .<br/>
                                Artconomy is based in the United States of America.
                              </p>
                            </v-col>
                          </v-card-text>
                        </v-window-item>
                        <v-window-item>
                          <ac-paginated :list="readers">
                            <template v-slot:default>
                              <ac-form-container v-bind="readerForm.bind">
                                <v-row no-gutters>
                                  <v-col cols="12" md="6" offset-md="3">
                                    <v-card elevation="10">
                                      <v-card-text>
                                        <v-row>
                                          <v-col v-for="reader in readers.list" :key="reader.x!.id" cols="12">
                                            <v-radio-group v-model="readerForm.fields.reader.model">
                                              <ac-bound-field
                                                  field-type="v-radio"
                                                  :field="readerForm.fields.reader"
                                                  :value="reader.x!.id"
                                                  :label="reader.x!.name"
                                              />
                                            </v-radio-group>
                                          </v-col>
                                          <v-col cols="12" @click="paymentSubmit">
                                            <v-btn color="green" variant="flat" block>Activate Reader</v-btn>
                                          </v-col>
                                        </v-row>
                                      </v-card-text>
                                    </v-card>
                                  </v-col>
                                </v-row>
                              </ac-form-container>
                            </template>
                          </ac-paginated>
                        </v-window-item>
                        <v-window-item>
                          <v-row>
                            <v-col cols="12" md="6" offset-md="3" class="pa-5">
                              <v-btn color="primary" block variant="flat" @click="paymentSubmit">
                                Mark Paid by Cash
                              </v-btn>
                            </v-col>
                          </v-row>
                        </v-window-item>
                      </v-window>
                    </template>
                  </ac-load-section>
                </v-col>
              </v-row>
            </ac-form-dialog>
          </v-col>
          <v-col cols="12" v-if="isStaff" class="pt-5 transactions-list">
            <ac-paginated :list="transactions">
              <template v-slot:default>
                <v-row>
                  <v-col cols="12">
                    <v-list three-line>
                      <template v-for="transaction, index in transactions.list" :key="transaction.x.id">
                        <ac-transaction :transaction="transaction.x" :username="username" :current-account="300"/>
                        <v-divider v-if="index + 1 < transactions.list.length" :key="index"/>
                      </template>
                    </v-list>
                  </v-col>
                </v-row>
              </template>
            </ac-paginated>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import Viewer from '@/mixins/viewer.ts'
import {Decimal} from 'decimal.js'
import {SingleController} from '@/store/singles/controller.ts'
import Invoice from '@/types/Invoice.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Formatting from '@/mixins/formatting.ts'
import {ListController} from '@/store/lists/controller.ts'
import LineItem from '@/types/LineItem.ts'
import AcLineItemListing from '@/components/price_preview/AcLineItemListing.vue'
import {InvoiceStatus} from '@/types/InvoiceStatus.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcInvoiceStatus from '@/components/AcInvoiceStatus.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import StripeHostMixin from '@/components/views/order/mixins/StripeHostMixin.ts'
import {reckonLines} from '@/lib/lineItemFunctions.ts'
import {BASE_URL, baseCardSchema, INVOICE_TYPES} from '@/lib/lib.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import Transaction from '@/types/Transaction.ts'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import {profileLink} from '@/lib/otherFormatters.ts'

@Component({
  components: {
    AcTransaction,
    AcAvatar,
    AcLink,
    AcPaginated,
    AcBoundField,
    AcCardManager,
    AcFormDialog,
    AcFormContainer,
    AcInvoiceStatus,
    AcLineItemListing,
    AcLoadSection,
  },
})
class InvoiceDetail extends mixins(Subjective, Viewer, Formatting, StripeHostMixin) {
  @Prop({required: true})
  public invoiceId!: string

  public invoice = null as unknown as SingleController<Invoice>
  public lineItems = null as unknown as ListController<LineItem>
  public transactions = null as unknown as ListController<Transaction>
  public stateChange = null as unknown as FormController
  public showPayment = false
  public cardTabs = 0
  public INVOICE_TYPES = INVOICE_TYPES
  public profileLink = profileLink
  public logo = new URL('/static/images/logo.svg', BASE_URL).href

  DRAFT = InvoiceStatus.DRAFT
  OPEN = InvoiceStatus.OPEN

  @Watch('cardTabs')
  public clearManualTransactionSettings(tabValue: number) {
    // TODO: Find a good way to deduplicate this code fragment from DeliverablePayment
    if (tabValue === 2) {
      this.paymentForm.fields.cash.update(true)
    } else {
      this.paymentForm.fields.cash.update(false)
    }
    if ((tabValue === 1) && this.readers.list.length) {
      if (!this.readerForm.fields.reader.value) {
        this.readerForm.fields.reader.update(this.readers.list[0].x!.id)
      }
      this.paymentForm.fields.use_reader.update(true)
    } else {
      this.paymentForm.fields.use_reader.update(false)
    }
    this.updateIntent()
  }

  public get editable() {
    return this.isStaff && this.invoice.x!.status === InvoiceStatus.DRAFT
  }

  public statusEndpoint(append: string) {
    this.stateChange.endpoint = `${this.url}${append}/`
    this.stateChange.submit()
  }

  get url() {
    return `/api/sales/invoice/${this.invoiceId}/`
  }

  get totalCharge() {
    if (!this.lineItems || (this.lineItems.list.length === 0)) {
      return new Decimal('0.00')
    }
    return reckonLines(this.lineItems.list.map((item) => item.x as LineItem))
  }

  @Watch('totalCharge')
  public updateForLines(newVal: Decimal, oldVal: Decimal) {
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
    return invoice.status === InvoiceStatus.OPEN
  }

  @Watch('invoice.x')
  public enableIntent(invoice: null | Invoice) {
    this.updateIntent()
    if (invoice && invoice.status !== InvoiceStatus.OPEN) {
      this.showPayment = false
    }
  }

  public get readerFormUrl() {
    return `${this.invoice?.endpoint}stripe-process-present-card/`
  }

  @Watch('readers.ready')
  public setTab(val: boolean) {
    if (val && this.isStaff && this.readers.list.length) {
      this.cardTabs = 1
    }
  }

  public paymentSubmit() {
    this.paymentForm.clearErrors()
    if (this.paymentForm.fields.cash.value) {
      this.paymentForm.submit()
    } else if (this.paymentForm.fields.use_reader.value) {
      this.readerForm.submit().catch((error) => {
        this.readerForm.setErrors(error)
      })
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
    this.stateChange = this.$getForm(`${this.prefix}__stateChange`, {
      endpoint: this.url,
      fields: {},
    })
    this.invoice = this.$getSingle(`${this.prefix}`, {
      endpoint: this.url,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'Invoice',
        serializer: 'InvoiceSerializer',
      },
    })
    // Fix the form, since it will be null on upstream's creation.
    this.readerForm.endpoint = this.readerFormUrl
    this.invoice.get()
    this.lineItems = this.$getList(`${this.prefix}__line_items`, {
      endpoint: `/api/sales/invoice/${this.invoiceId}/line-items/`,
      paginated: false,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'LineItem',
        serializer: 'LineItemSerializer',
        list: {
          appLabel: 'sales',
          modelName: 'Invoice',
          pk: `${this.invoiceId}`,
          listName: 'line_items',
        },
      },
    })
    this.lineItems.firstRun()
    this.transactions = this.$getList(`${this.prefix}__transaction_records`, {
      endpoint: `/api/sales/invoice/${this.invoiceId}/transaction-records/`,
    })
    this.transactions.get().catch(this.statusOk(403))
  }
}

export default toNative(InvoiceDetail)
</script>
