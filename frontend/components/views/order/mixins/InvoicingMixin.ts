import { invoiceLines } from "@/lib/lineItemFunctions.ts"
import { FormController } from "@/store/forms/form-controller.ts"
import { computed, ComputedRef, watch } from "vue"
import { useSingle } from "@/store/singles/hooks.ts"
import { usePricing } from "@/mixins/PricingAware.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useRouter } from "vue-router"
import type { Deliverable, LineItem, Product } from "@/types/main"

declare interface UseInvoicingArgs {
  newInvoice: FormController
  sellerName: ComputedRef<string>
  planName: ComputedRef<string>
  international: ComputedRef<boolean>
  invoiceEscrowEnabled: ComputedRef<boolean>
}

export const useInvoicing = ({
  newInvoice,
  sellerName,
  planName,
  international,
  invoiceEscrowEnabled,
}: UseInvoicingArgs) => {
  const router = useRouter()
  const { pricing } = usePricing()
  const invoiceProduct = useSingle<Product>("invoiceProduct", { endpoint: "" })
  const invoiceLineItems = useList<LineItem>("newInvoiceLines", {
    endpoint: "#",
    paginated: false,
  })

  const rawInvoiceLineItems = computed(() => {
    return invoiceLines({
      planName: planName.value,
      cascade: newInvoice.fields.cascade_fees.value,
      pricing: pricing.x || null,
      international: international.value,
      escrowEnabled: invoiceEscrowEnabled.value,
      product: invoiceProduct.x || null,
      value: newInvoice.fields.price.value,
    })
  })

  const goToOrder = (deliverable: Deliverable) => {
    router.push({
      name: "SaleDeliverableOverview",
      params: {
        username: sellerName.value,
        orderId: deliverable.order.id + "",
        deliverableId: deliverable.id + "",
      },
    })
  }

  watch(rawInvoiceLineItems, (newValue: LineItem[]) => {
    invoiceLineItems.ready = true
    invoiceLineItems.setList(newValue || [])
  })

  watch(
    () => newInvoice.fields.product.value,
    (val: undefined | null | number) => {
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
    },
  )
  watch(
    () => invoiceProduct.x,
    (val: Product | null) => {
      /* istanbul ignore if */
      if (!val) {
        return
      }
      newInvoice.fields.price.update(val.starting_price)
      newInvoice.fields.task_weight.update(val.task_weight)
      newInvoice.fields.revisions.update(val.revisions)
      newInvoice.fields.expected_turnaround.update(val.expected_turnaround)
      newInvoice.fields.cascade_fees.update(val.cascade_fees)
    },
  )
  return {
    invoiceProduct,
    invoiceLineItems,
    goToOrder,
  }
}
