import {CreditCardToken} from '@/types/CreditCardToken.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import ClientSecret from '@/types/ClientSecret.ts'
import debounce from 'lodash/debounce'
import StripeReader from '@/types/StripeReader.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {ComputedRef, watch, Ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'


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
