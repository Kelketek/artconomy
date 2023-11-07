<template>
  <v-chip :color="STATUSES[invoice.status].color" :light="!STATUSES[invoice.status].dark" variant="flat" small>
    <v-icon left icon="{{STATUSES[invoice.status].icon}}"/>
    {{STATUSES[invoice.status].text}}
  </v-chip>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import Invoice from '@/types/Invoice'

@Component
class AcInvoiceStatus extends Vue {
  public STATUSES = {
    0: {
      text: 'Draft',
      icon: 'edit_note',
      color: 'white',
      dark: false,
    },
    1: {
      text: 'Open',
      icon: 'star',
      color: 'primary',
      dark: true,
    },
    2: {
      text: 'Paid',
      icon: 'paid',
      color: 'green',
      dark: true,
    },
    5: {
      text: 'Void',
      icon: 'block',
      color: 'black',
      dark: true,
    },
  }

  @Prop({required: true})
  public invoice!: Invoice
}

export default toNative(AcInvoiceStatus)
</script>
