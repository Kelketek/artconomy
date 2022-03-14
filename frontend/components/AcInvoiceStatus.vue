<template>
  <v-chip :color="STATUSES[invoice.status].color" :light="!STATUSES[invoice.status].dark" small>
    <v-icon left>{{STATUSES[invoice.status].icon}}</v-icon>
    {{STATUSES[invoice.status].text}}
  </v-chip>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Invoice from '@/types/Invoice'

@Component
export default class AcInvoiceStatus extends Vue {
  public STATUSES = {
    0: {text: 'Draft', icon: 'edit_note', color: 'white', dark: false},
    1: {text: 'Open', icon: 'star', color: 'primary', dark: true},
    2: {text: 'Paid', icon: 'paid', color: 'green', dark: true},
    5: {text: 'Void', icon: 'block', color: 'black', dark: true},
  }

  @Prop({required: true})
  public invoice!: Invoice
}
</script>
