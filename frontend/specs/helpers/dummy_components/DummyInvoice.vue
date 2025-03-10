<template>
  <ac-invoice-form
    :new-invoice="newInvoice"
    :username="username"
    :line-items="invoiceLineItems"
    :escrow-enabled="invoiceEscrowEnabled"
    :show-buyer="showBuyer"
  />
</template>

<script setup lang="ts">
import AcInvoiceForm from '@/components/views/orders/AcInvoiceForm.vue'
import {baseInvoiceSchema} from '@/lib/lib.ts'
import {useInvoicing} from '@/components/views/order/mixins/InvoicingMixin.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {computed} from 'vue'

const props = defineProps<{ username: string, invoiceEscrowEnabled: boolean, showBuyer: boolean }>()

const newInvoice = useForm('invoice', baseInvoiceSchema('/test/'))

const sellerName = computed(() => {
  return props.username
})

const international = computed(() => {
  return false
})

const planName = computed(() => {
  return 'Basic'
})

const computedInvoiceEscrowEnabled = computed(() => props.invoiceEscrowEnabled)

// invoiceProduct and goToOrder used in tests.
const {invoiceLineItems, invoiceProduct, goToOrder} = useInvoicing({
  newInvoice,
  sellerName,
  planName,
  international,
  invoiceEscrowEnabled: computedInvoiceEscrowEnabled,
})
defineExpose({invoiceLineItems, invoiceProduct, goToOrder})
</script>
