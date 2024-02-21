import {Component, Watch} from 'vue-facing-decorator'
import Product from '@/types/Product.ts'
import Deliverable from '@/types/Deliverable.ts'
import {invoiceLines} from '@/lib/lineItemFunctions.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Pricing from '@/types/Pricing.ts'
import {ArtVue} from '@/lib/lib.ts'
import LineItem from '@/types/LineItem.ts'
import {ListController} from '@/store/lists/controller.ts'
import {computed, ComputedRef, Ref, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {usePricing} from '@/mixins/PricingAware.ts'
import {useList} from '@/store/lists/hooks.ts'

@Component
export default class InvoicingMixin extends ArtVue {
  public newInvoice!: FormController
  /** Defined in child **/
  declare public sellerName: string
  declare public invoiceEscrowEnabled: boolean
  declare public international: boolean

  public invoiceProduct: SingleController<Product> = null as unknown as SingleController<Product>
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public invoiceLineItems = null as unknown as ListController<LineItem>

  @Watch('newInvoice.fields.product.value')
  public updateProduct(val: undefined | null | number) {
    /* istanbul ignore if */
    if (val === undefined) {
      return
    }
    if (!val) {
      this.invoiceProduct.kill()
      this.invoiceProduct.setX(null)
      return
    }
    this.invoiceProduct.endpoint = `/api/sales/account/${this.sellerName}/products/${val}/`
    this.invoiceProduct.kill()
    this.invoiceProduct.get()
  }

  @Watch('invoiceProduct.x', {deep: true})
  public updatePrice(val: Product | null) {
    /* istanbul ignore if */
    if (!val) {
      return
    }
    this.newInvoice.fields.price.update(val.starting_price)
    this.newInvoice.fields.task_weight.update(val.task_weight)
    this.newInvoice.fields.revisions.update(val.revisions)
    this.newInvoice.fields.expected_turnaround.update(val.expected_turnaround)
    this.newInvoice.fields.cascade_fees.update(val.cascade_fees)
  }

  public goToOrder(deliverable: Deliverable) {
    this.$router.push({
      name: 'SaleDeliverableOverview',
      params: {
        username: this.sellerName,
        orderId: deliverable.order.id + '',
        deliverableId: deliverable.id + '',
      },
    })
  }

  /* istanbul ignore next */
  public get planName(): string | null {
    // Must be implemented by child. Get the plan name whose prices apply here.
    return null
  }

  public get rawInvoiceLineItems() {
    if (!this.newInvoice) {
      return []
    }
    return invoiceLines({
      planName: this.planName,
      cascade: this.newInvoice.fields.cascade_fees.value,
      pricing: (this.pricing.x || null),
      international: this.international,
      escrowEnabled: this.invoiceEscrowEnabled,
      product: (this.invoiceProduct.x || null),
      value: this.newInvoice.fields.price.value,
    })
  }

  @Watch('rawInvoiceLineItems')
  public updateLineItems(newValue: LineItem[]) {
    this.invoiceLineItems.ready = true
    this.invoiceLineItems.setList(newValue || [])
  }

  public created() {
    this.invoiceLineItems = this.$getList('newInvoiceLines', {
      endpoint: '#',
      paginated: false,
    })
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/pricing-info/'})
    this.pricing.get()
    this.invoiceProduct = this.$getSingle('invoiceProduct', {endpoint: ''})
  }
}


declare interface UseInvoicingArgs {
  newInvoice: FormController,
  sellerName: ComputedRef<string>,
  planName: ComputedRef<string>,
  international: ComputedRef<boolean>,
  invoiceEscrowEnabled: ComputedRef<boolean>,
}

export const useInvoicing = ({
  newInvoice, sellerName, planName, international, invoiceEscrowEnabled
}: UseInvoicingArgs) => {

  const {pricing} = usePricing()
  const invoiceProduct = useSingle<Product>('invoiceProduct', {endpoint: ''})
  const invoiceLineItems = useList<LineItem>('newInvoiceLines', {
    endpoint: '#',
    paginated: false,
  })

  const rawInvoiceLineItems = computed(() => {
    return invoiceLines({
      planName: planName.value,
      cascade: newInvoice.fields.cascade_fees.value,
      pricing: (pricing.x || null),
      international: international.value,
      escrowEnabled: invoiceEscrowEnabled.value,
      product: (invoiceProduct.x || null),
      value: newInvoice.fields.price.value,
    })
  })

  watch(rawInvoiceLineItems, (newValue: LineItem[]) => {
    invoiceLineItems.ready = true
    invoiceLineItems.setList(newValue || [])
  })

  watch(() => newInvoice.fields.product.value, (val: undefined | null | number) => {
    if (val === undefined) {
      return
    }
    if (!val) {
      invoiceProduct.kill()
      invoiceProduct.setX(null)
      return
    }
    invoiceProduct.endpoint = `/api/sales/account/${sellerName.value}/products/${val}/`
    invoiceProduct.kill()
    invoiceProduct.get().then()
  })
  watch(() => invoiceProduct.x, (val: Product|null) => {
    /* istanbul ignore if */
    if (!val) {
      return
    }
    newInvoice.fields.price.update(val.starting_price)
    newInvoice.fields.task_weight.update(val.task_weight)
    newInvoice.fields.revisions.update(val.revisions)
    newInvoice.fields.expected_turnaround.update(val.expected_turnaround)
    newInvoice.fields.cascade_fees.update(val.cascade_fees)
  })
  return {
    invoiceProduct,
    invoiceLineItems,
  }
}
