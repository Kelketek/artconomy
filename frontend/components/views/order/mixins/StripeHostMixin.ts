import {Component, mixins, Watch} from 'vue-facing-decorator'
import {CreditCardToken} from '@/types/CreditCardToken.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import ClientSecret from '@/types/ClientSecret.ts'
import debounce from 'lodash/debounce'
import {ListController} from '@/store/lists/controller.ts'
import StripeReader from '@/types/StripeReader.ts'
import ErrorHandling, {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {ComputedRef, watch, Ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'

@Component
export default class StripeHostMixin extends mixins(ErrorHandling) {
  public paymentForm!: FormController
  // clientSecret must be provided by the inheriting component.
  public clientSecret!: SingleController<ClientSecret>
  public readers = null as unknown as ListController<StripeReader>
  public reader = null as unknown as SingleController<StripeReader>
  public readerForm = null as unknown as FormController

  // Override this if fetching the secret isn't immediately possible.
  public get canUpdate() {
    /* istanbul ignore next */
    return true
  }

  public rawUpdateIntent() {
    this.clientSecret.post(this.paymentForm.rawData).then(
      this.clientSecret.setX).then(
      () => {
        this.clientSecret.ready = true
      },
    ).catch(() => {
    }).finally(() => {
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
  public stripeCardUpdated(value: CreditCardToken | null) {
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

  public get readerFormUrl(): string {
    /* istanbul ignore next */
    throw Error('Not implemented')
  }

  public created() {
    this.readers = this.$getList(
      'stripeReaders', {
        endpoint: '/api/sales/stripe-readers/',
        persistent: true,
      },
    )
    if (!(this.readers.ready || this.readers.fetching || this.readers.failed)) {
      this.readers.get().catch(this.statusOk(403))
    }
    this.readerForm = this.$getForm('stripeReader', {
      endpoint: `${this.readerFormUrl}`,
      reset: false,
      fields: {
        reader: {value: null},
      },
    })
  }
}

export interface StripeHostArgs {
  clientSecret: SingleController<ClientSecret>,
  readerFormUrl: ComputedRef<string>,
  canUpdate: ComputedRef<boolean>|Ref<boolean>,
  paymentForm: FormController,
}

export const useStripeHost = ({clientSecret, readerFormUrl, canUpdate, paymentForm}: StripeHostArgs) => {
  const readers = useList<StripeReader>(
    'stripeReaders', {
      endpoint: '/api/sales/stripe-readers/',
      persistent: true,
    },
  )
  const {statusOk} = useErrorHandling()
  if (!(readers.ready || readers.fetching || readers.failed)) {
    readers.get().catch(statusOk(403))
  }
  const readerForm = useForm('stripeReader', {
    endpoint: readerFormUrl.value,
    reset: false,
    fields: {
      reader: {value: null},
    },
  })
  watch(readerFormUrl, (newEndpoint) => {readerForm.endpoint = newEndpoint})
  const rawUpdateIntent = () => {
    clientSecret.post(paymentForm.rawData).then(
      clientSecret.setX).then(
      () => {
        clientSecret.ready = true
      },
    ).catch(() => {
    }).finally(() => {
      paymentForm.sending = false
    })
  }
  const debouncedUpdateIntent = debounce(rawUpdateIntent, 250, {trailing: true})
  const updateIntent = () => {
    if (!canUpdate.value) {
      return
    }
    paymentForm.sending = true
    debouncedUpdateIntent()
  }
  watch(() => paymentForm.fields.card_id.value, (value: CreditCardToken|null) => {
    if (value) {
      clientSecret.params = {card_id: value.id}
    } else {
      clientSecret.params = {}
    }
    updateIntent()
  })
  watch(() => paymentForm.fields.save_card.value, updateIntent)
  watch(() => paymentForm.fields.make_primary.value, updateIntent)
  return {
    readerForm,
    paymentForm,
    readers,
    rawUpdateIntent,
    updateIntent,
    debouncedUpdateIntent,
  }
}
