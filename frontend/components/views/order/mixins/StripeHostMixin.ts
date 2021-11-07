import Component from 'vue-class-component'
import Vue from 'vue'
import {CreditCardToken} from '@/types/CreditCardToken'
import {Watch} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import {SingleController} from '@/store/singles/controller'
import ClientSecret from '@/types/ClientSecret'

@Component
export default class StripeHostMixin extends Vue {
  public paymentForm!: FormController
  public clientSecret!: SingleController<ClientSecret>
  public updateIntent() {
    this.paymentForm.sending = true
    this.clientSecret.post(this.paymentForm.rawData).then(
      this.clientSecret.setX).then(
      () => { this.clientSecret.ready = true },
    ).catch(() => {}).finally(() => {
      this.paymentForm.sending = false
    })
  }

  @Watch('paymentForm.fields.card_id.value')
  public stripeCardUpdated(value: CreditCardToken|null) {
    if (value) {
      this.clientSecret.params = {card_id: value.id}
    } else {
      this.clientSecret.params = {}
    }
    this.updateIntent()
  }

  @Watch('paymentForm.fields.save_card.value')
  public saveCardUpdate() {
    this.updateIntent()
  }

  @Watch('paymentForm.fields.make_primary.value')
  public makePrimaryUpdate() {
    this.updateIntent()
  }
}