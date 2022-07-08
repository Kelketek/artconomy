import Component from 'vue-class-component'
import Vue from 'vue'
import {CreditCardToken} from '@/types/CreditCardToken'
import {Watch} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import {SingleController} from '@/store/singles/controller'
import ClientSecret from '@/types/ClientSecret'
import debounce from 'lodash/debounce'
import {ListController} from '@/store/lists/controller'
import StripeReader from '@/types/StripeReader'

@Component
export default class StripeHostMixin extends Vue {
  public paymentForm!: FormController
  public clientSecret!: SingleController<ClientSecret>
  public readers = null as unknown as ListController<StripeReader>
  public reader = null as unknown as SingleController<StripeReader>
  public readerForm = null as unknown as FormController

  // Override this if fetching the secret isn't immediately possible.
  public get canUpdate() {
    return true
  }

  public rawUpdateIntent() {
    this.clientSecret.post(this.paymentForm.rawData).then(
      this.clientSecret.setX).then(
      () => { this.clientSecret.ready = true },
    ).catch(() => {}).finally(() => {
      this.paymentForm.sending = false
    })
  }

  public get debouncedUpdateIntent() {
    return debounce(this.rawUpdateIntent, 250, {trailing: true})
  }

  public updateIntent() {
    if (!this.canUpdate) {
      return
    }
    this.paymentForm.sending = true
    this.debouncedUpdateIntent()
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

  public fetchReaders() {
    this.readers.fetching = true
  }

  public get readerFormUrl(): string {
    throw Error('Not implemented')
  }

  public created() {
    this.readers = this.$getList(
      'stripeReaders', {endpoint: '/api/sales/v1/stripe-readers/', persistent: true},
    )
    this.readers.firstRun()
    this.readerForm = this.$getForm('stripeReader', {
      endpoint: `${this.readerFormUrl}`,
      reset: false,
      fields: {
        reader: {value: null},
      },
    })
  }
}
