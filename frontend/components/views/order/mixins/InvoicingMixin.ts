import Vue from 'vue'
import Component from 'vue-class-component'
import {Watch} from 'vue-property-decorator'
import Product from '@/types/Product'
import Deliverable from '@/types/Deliverable'
import {invoiceLines} from '@/lib/lineItemFunctions'
import {FormController} from '@/store/forms/form-controller'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'

@Component
export default class InvoicingMixin extends Vue {
  public newInvoice!: FormController
  public sellerName!: string
  public invoiceEscrowDisabled!: boolean

  public invoiceProduct: SingleController<Product> = null as unknown as SingleController<Product>
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>

  @Watch('newInvoice.fields.product.value')
  public updateProduct(val: undefined|null|number) {
    /* istanbul ignore if */
    if (val === undefined) {
      return
    }
    if (!val) {
      this.invoiceProduct.kill()
      this.invoiceProduct.setX(null)
      return
    }
    this.invoiceProduct.endpoint = `/api/sales/v1/account/${this.sellerName}/products/${val}/`
    this.invoiceProduct.kill()
    this.invoiceProduct.get()
  }

  @Watch('invoiceProduct.x', {deep: true})
  public updatePrice(val: Product|null) {
    /* istanbul ignore if */
    if (!val) {
      return
    }
    this.newInvoice.fields.price.update(val.starting_price)
    this.newInvoice.fields.task_weight.update(val.task_weight)
    this.newInvoice.fields.revisions.update(val.revisions)
    this.newInvoice.fields.expected_turnaround.update(val.expected_turnaround)
  }

  public goToOrder(deliverable: Deliverable) {
    this.$router.push({
      name: 'SaleDeliverableOverview',
      params: {username: this.sellerName, orderId: deliverable.order.id + '', deliverableId: deliverable.id + ''},
    })
  }

  public get invoiceLineItems() {
    const linesController = this.$getList('newInvoiceLines', {endpoint: '#', paginated: false})
    linesController.ready = true
    linesController.setList(invoiceLines({
      pricing: (this.pricing.x || null),
      escrowDisabled: this.invoiceEscrowDisabled,
      product: (this.invoiceProduct.x || null),
      value: this.newInvoice.fields.price.value,
    }))
    return linesController
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
    this.pricing.get()
    this.invoiceProduct = this.$getSingle('invoiceProduct', {endpoint: ''})
  }
}
