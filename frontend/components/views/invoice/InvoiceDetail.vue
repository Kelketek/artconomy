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
                        <v-col class="text-center" v-if="powers.table_seller && (invoice.x.status === InvoiceStatus.DRAFT)">
                          <v-btn color="primary" variant="flat" @click="() => statusEndpoint('finalize')">Finalize</v-btn>
                        </v-col>
                        <v-col class="text-center" v-if="invoice.x.status === InvoiceStatus.OPEN && !invoice.x.record_only">
                          <v-btn color="green" variant="flat" @click="() => showPayment = true">Pay</v-btn>
                        </v-col>
                        <v-col class="text-center" v-if="powers.table_seller && (([InvoiceStatus.DRAFT, InvoiceStatus.OPEN] as InvoiceStatusValue[]).includes(invoice.x.status))">
                          <v-btn color="danger" variant="flat" @click="() => statusEndpoint('void')">Void</v-btn>
                        </v-col>
                      </v-row>
                      <v-row v-if="invoice.x.record_only && invoice.x.status === InvoiceStatus.OPEN">
                        <v-col>
                          <v-alert type="info">
                            This invoice is for record purposes only and cannot be paid through this site. You must
                            contact your artist for information on how to pay the amount due.
                          </v-alert>
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
                <v-col class="text-center" cols="12">Total Charge: <strong>${{ totalCharge }}</strong>
                </v-col>
                <v-col cols="12">
                  <ac-load-section :controller="invoice">
                    <template v-slot:default>
                      <v-tabs v-model="cardTabs" class="mb-2" fixed-tabs v-if="powers.table_seller">
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
          <v-col cols="12" v-if="powers.view_financials" class="pt-5 transactions-list">
            <ac-paginated :list="transactions">
              <template v-slot:default>
                <v-row>
                  <v-col cols="12">
                    <v-list three-line>
                      <template v-for="transaction, index in transactions.list" :key="transaction.x!.id">
                        <ac-transaction :transaction="transaction.x!" :username="username" :current-account="300"/>
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

<script setup lang="ts">
import {computed, ref, watch} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcLineItemListing from '@/components/price_preview/AcLineItemListing.vue'
import {InvoiceStatus} from '@/types/enums/InvoiceStatus.ts'
import AcInvoiceStatus from '@/components/AcInvoiceStatus.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {useStripeHost} from '@/components/views/order/mixins/StripeHostMixin.ts'
import {reckonLines} from '@/lib/lineItemFunctions.ts'
import {BASE_URL, baseCardSchema, INVOICE_TYPES} from '@/lib/lib.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcCardManager from '@/components/views/settings/payment/AcCardManager.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import {formatDateTime, profileLink} from '@/lib/otherFormatters.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'

import type {ClientSecret, Invoice, InvoiceStatusValue, LineItem, SubjectiveProps, Transaction} from '@/types/main'

const props = defineProps<{invoiceId: string} & SubjectiveProps>()
const {powers} = useViewer()

const showPayment = ref(false)
const cardTabs = ref(0)
const logo = new URL('/static/images/logo.svg', BASE_URL).href

const url = computed(() => `/api/sales/invoice/${props.invoiceId}/`)
const cardManager = ref<null|typeof AcCardManager>(null)

const schema = baseCardSchema(`${url.value}pay/`)
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

const prefix = computed(() => `invoice__${props.invoiceId}`)
const editable = computed(() => powers.value.table_seller && (invoice.x?.status === InvoiceStatus.DRAFT))
const paymentForm = useForm(`${prefix.value}__payment`, schema)
const clientSecret = useSingle<ClientSecret>(`${prefix.value}__clientSecret`, {endpoint: `${url.value}payment-intent/`})
const stateChange = useForm(`${prefix.value}__stateChange`, {
  endpoint: url.value,
  fields: {},
})
const invoice = useSingle<Invoice>(`${prefix.value}`, {
  endpoint: url.value,
  socketSettings: {
    appLabel: 'sales',
    modelName: 'Invoice',
    serializer: 'InvoiceSerializer',
  },
})
invoice.get()
const statusEndpoint = (append: string) => {
  stateChange.endpoint = `${url.value}${append}/`
  stateChange.submit()
}
const lineItems = useList<LineItem>(`${prefix.value}__line_items`, {
  endpoint: `/api/sales/invoice/${props.invoiceId}/line-items/`,
  paginated: false,
  socketSettings: {
    appLabel: 'sales',
    modelName: 'LineItem',
    serializer: 'LineItemSerializer',
    list: {
      appLabel: 'sales',
      modelName: 'Invoice',
      pk: `${props.invoiceId}`,
      listName: 'line_items',
    },
  },
})
lineItems.firstRun()
const transactions = useList<Transaction>(`${prefix.value}__transaction_records`, {
  endpoint: `/api/sales/invoice/${props.invoiceId}/transaction-records/`,
})
const {statusOk} = useErrorHandling()
transactions.get().catch(statusOk(403))
const readerFormUrl = computed(() => `${invoice?.endpoint}stripe-process-present-card/`)
const canUpdate = computed(() => {
  if (paymentForm.fields.cash.value) {
    return false
  }
  if (!invoice.x) {
    return false
  }
  return invoice.x.status === InvoiceStatus.OPEN
})

const {readerForm, updateIntent, readers} = useStripeHost({clientSecret, readerFormUrl, canUpdate, paymentForm})

const paymentSubmit = () => {
  paymentForm.clearErrors()
  if (paymentForm.fields.cash.value) {
    paymentForm.submit()
  } else if (paymentForm.fields.use_reader.value) {
    readerForm.submit().catch((error) => {
      readerForm.setErrors(error)
    })
  } else {
    cardManager.value?.stripeSubmit()
  }
}

const totalCharge = computed(() => {
  if (lineItems.list.length === 0) {
    return '0.00'
  }
  return reckonLines(lineItems.list.map((item) => item.x as LineItem))
})

watch(cardTabs, (tabValue) => {
  // TODO: Find a good way to deduplicate this code fragment from DeliverablePayment
  if (tabValue === 2) {
    paymentForm.fields.cash.update(true)
  } else {
    paymentForm.fields.cash.update(false)
  }
  if ((tabValue === 1) && readers.list.length) {
    if (!readerForm.fields.reader.value) {
      readerForm.fields.reader.update(readers.list[0].x!.id)
    }
    paymentForm.fields.use_reader.update(true)
  } else {
    paymentForm.fields.use_reader.update(false)
  }
  updateIntent()
})

watch(totalCharge, (newVal: string, oldVal: string) => {
  paymentForm.fields.amount.model = newVal.toString()
  if (parseFloat(newVal) === parseFloat(oldVal)) {
    return
  }
  updateIntent()
})

watch(() => readers.ready, (val) => {
  if (val && powers.value.table_seller && readers.list.length) {
    cardTabs.value = 1
  }
})

watch(() => invoice.x, (invoice: null | Invoice) => {
  updateIntent()
  if (invoice && invoice.status !== InvoiceStatus.OPEN) {
    showPayment.value = false
  }
})
</script>
