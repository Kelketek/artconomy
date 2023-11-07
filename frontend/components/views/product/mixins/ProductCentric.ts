import Subjective from '@/mixins/subjective'
import {Component, mixins, Prop} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller'
import Product from '@/types/Product'
import {addBusinessDays, formatISO} from 'date-fns'

@Component
export default class ProductCentric extends mixins(Subjective) {
  @Prop({required: true})
  public productId!: number

  public product: SingleController<Product> = null as unknown as SingleController<Product>

  public get url() {
    return `/api/sales/account/${this.username}/products/${this.productId}/`
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
