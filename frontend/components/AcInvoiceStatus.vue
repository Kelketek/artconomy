<template>
  <v-chip :color="STATUSES[invoice.status].color" :light="!STATUSES[invoice.status].dark" variant="flat" size="small">
    <v-icon left :icon="STATUSES[invoice.status].icon"/>
    {{STATUSES[invoice.status].text}}
  </v-chip>
</template>

<script setup lang="ts">
import Invoice from '@/types/Invoice.ts'
import {mdiInvoiceCheck, mdiInvoiceTextEdit, mdiInvoiceTextRemove, mdiStar} from '@mdi/js'

const props = defineProps<{invoice: Invoice}>()
const STATUSES = {
  0: {
    text: 'Draft',
    icon: mdiInvoiceTextEdit,
    color: 'white',
    dark: false,
  },
  1: {
    text: 'Open',
    icon: mdiStar,
    color: 'primary',
    dark: true,
  },
  2: {
    text: 'Paid',
    icon: mdiInvoiceCheck,
    color: 'green',
    dark: true,
  },
  5: {
    text: 'Void',
    icon: mdiInvoiceTextRemove,
    color: 'black',
    dark: true,
  },
}
</script>
