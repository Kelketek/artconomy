import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import Product from '@/types/Product'
import moment, {Moment} from 'moment-business-days'
import {Prop} from 'vue-property-decorator'

@Component
export default class ProductCentric extends mixins(Subjective) {
  @Prop({required: true})
  public productId!: number

  public product: SingleController<Product> = null as unknown as SingleController<Product>

  public get url() {
    return `/api/sales/v1/account/${this.username}/products/${this.productId}/`
  }

  public get deliveryDate() {
    const product = this.product.x as Product
    // @ts-ignore
    return (moment() as Moment).businessAdd(Math.ceil(product.expected_turnaround))
  }

  public created() {
    this.product = this.$getSingle(`product__${this.productId}`, {endpoint: this.url})
  }
}
