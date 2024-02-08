<template>
  <ac-invoice-form :new-invoice="newInvoice" :username="username" :line-items="invoiceLineItems" :escrow-enabled="invoiceEscrowEnabled" :show-buyer="showBuyer" />
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcInvoiceForm from '@/components/views/orders/AcInvoiceForm.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {baseInvoiceSchema} from '@/lib/lib.ts'
import InvoicingMixin from '@/components/views/order/mixins/InvoicingMixin.ts'

@Component({
  components: {AcInvoiceForm},
})
class DummyInvoice extends mixins(InvoicingMixin) {
  public newInvoice = null as unknown as FormController
  @Prop({required: true})
  public username!: string

  @Prop({required: true})
  // @ts-ignore
  public invoiceEscrowEnabled!: boolean

  @Prop({required: true})
  public showBuyer!: boolean

  // @ts-ignore
  public get sellerName() {
    return this.username
  }

  // @ts-ignore
  public get international() {
    return false
  }

  public get planName() {
    return 'Basic'
  }

  public created() {
    this.newInvoice = this.$getForm('invoice', baseInvoiceSchema('/test/'))
  }
}
export default toNative(DummyInvoice)
</script>
