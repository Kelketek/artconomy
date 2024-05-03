import Subjective from '@/mixins/subjective.ts'
import {Component, mixins, Prop} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import Product from '@/types/Product.ts'
import {addBusinessDays, formatISO} from 'date-fns'
import {useSingle} from '@/store/singles/hooks.ts'
import {computed, watch} from 'vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import ProductProps from '@/types/ProductProps.ts'

@Component
export default class ProductCentric extends mixins(Subjective) {
  @Prop({required: true})
  public productId!: number

  public product: SingleController<Product> = null as unknown as SingleController<Product>

  public get url() {
    return getUrl(this.username, this.productId)
  }

  public get deliveryDate() {
    const product = this.product.x as Product
    // @ts-ignore
    return formatISO(addBusinessDays(new Date(), product.expected_turnaround))
  }

  public created() {
    this.product = this.$getSingle(`product__${this.productId}`, {endpoint: this.url})
  }
}

const getDeliveryDate = (product: Product) => {
  return formatISO(addBusinessDays(new Date(), product.expected_turnaround))
}

const getUrl = (username: string, productId: number) => {
  return `/api/sales/account/${username}/products/${productId}/`
}

export const useProduct = <T extends SubjectiveProps & ProductProps>(props: T) => {
  const url = computed(() => getUrl(props.username, parseInt(`${props.productId}`, 10)))
  const product = useSingle<Product>(`product__${props.productId}`, {endpoint: url.value})
  product.get().then()
  const deliveryDate = computed(() => product.x && getDeliveryDate(product.x))
  return {
    product,
    deliveryDate,
    url,
  }
}
