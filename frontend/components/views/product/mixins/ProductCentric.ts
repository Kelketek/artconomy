import { addBusinessDays, formatISO } from "date-fns"
import { useSingle } from "@/store/singles/hooks.ts"
import { computed, watch } from "vue"
import type { Product, ProductProps, SubjectiveProps } from "@/types/main"

export const useProduct = <T extends SubjectiveProps & ProductProps>(
  props: T,
) => {
  const url = computed(
    () => `/api/sales/account/${props.username}/products/${props.productId}/`,
  )
  const product = useSingle<Product>(`product__${props.productId}`, {
    endpoint: url.value,
  })
  product.get().then()
  const deliveryDate = computed(
    () =>
      product.x &&
      !product.x.wait_list &&
      formatISO(addBusinessDays(new Date(), product.x.expected_turnaround)),
  )
  const saleMode = computed({
    get: () => {
      return product.patchers.compare_at_price.model !== null
    },
    set: (val: boolean) => {
      if (val) {
        product.patchers.compare_at_price.model =
          product.patchers.base_price.model
      }
    },
  })
  // Note: This might have to be refactored to not be created each time if we have multiple calls on a page and the
  // logic gets much more complex, since it will be called multiple times.
  watch(
    () => product.x?.starting_price,
    (newPrice?: string) => {
      // A sale should always be lower than the original price.
      if (newPrice === undefined) {
        return
      }
      if (!product.patchers.compare_at_price.model) {
        return
      }
      if (
        parseFloat(product.x!.starting_price) >
        parseFloat(product.patchers.compare_at_price.model)
      ) {
        product.patchers.compare_at_price.model = product.x!.starting_price
      }
    },
  )
  return {
    product,
    saleMode,
    deliveryDate,
    url,
  }
}
