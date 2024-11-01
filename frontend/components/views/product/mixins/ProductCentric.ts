import {addBusinessDays, formatISO} from 'date-fns'
import {useSingle} from '@/store/singles/hooks.ts'
import {computed} from 'vue'
import type {Product, ProductProps, SubjectiveProps} from '@/types/main'


export const useProduct = <T extends SubjectiveProps & ProductProps>(props: T) => {
  const url = computed(() => `/api/sales/account/${props.username}/products/${props.productId}/`)
  const product = useSingle<Product>(`product__${props.productId}`, {endpoint: url.value})
  product.get().then()
  const deliveryDate = computed(() => product.x && !product.x.wait_list && formatISO(addBusinessDays(new Date(), product.x.expected_turnaround)))
  return {
    product,
    deliveryDate,
    url,
  }
}
