<template>
  <ac-invoice-form :new-invoice="newInvoice" :username="username" :line-items="invoiceLineItems" :escrow-disabled="invoiceEscrowDisabled" :show-buyer="showBuyer" />
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcInvoiceForm from '@/components/views/orders/AcInvoiceForm.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseInvoiceSchema} from '@/lib/lib'
import {Prop} from 'vue-property-decorator'
import InvoicingMixin from '@/components/views/order/mixins/InvoicingMixin'

@Component({
  components: {AcInvoiceForm},
})
export default class DummyInvoice extends mixins(InvoicingMixin) {
  public newInvoice = null as unknown as FormController
  @Prop({required: true})
  public username!: string

  @Prop({required: true})
  public invoiceEscrowDisabled!: boolean

  @Prop({required: true})
  public showBuyer!: boolean

  public get sellerName() {
    return this.username
  }

  public created() {
    this.newInvoice = this.$getForm('invoice', baseInvoiceSchema('/test/'))
  }
}
</script>
