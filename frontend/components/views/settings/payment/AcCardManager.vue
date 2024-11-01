<template>
  <v-row no-gutters>
    <v-col cols="12" v-if="subject && cards.ready">
      <v-row no-gutters>
        <v-col>
          <v-tabs v-if="cards.list.length" v-model="tab" fixed-tabs>
            <v-tab value="saved-cards" class="saved-card-tab">
              <v-icon :icon="mdiContentSave"/>
              Saved Cards
            </v-tab>
            <v-tab value="new-card" class="new-card-tab">
              <v-icon :icon="mdiCreditCard"/>
              New Card
            </v-tab>
          </v-tabs>
        </v-col>
      </v-row>
      <v-row no-gutters>
        <v-col cols="12">
          <v-window v-model="tab">
            <v-window-item value="saved-cards" eager>
              <v-row no-gutters>
                <v-col cols="12" sm="8" offset-sm="2" md="6" offset-md="3" lg="4" offset-lg="4">
                  <ac-saved-card-field v-if="fieldMode" :model-value="modelValue" @input="setCard" :cards="cards"/>
                  <ac-card v-else v-for="card in cards.list" :card="card" :key="card.x!.id" :card-list="cards"/>
                </v-col>
              </v-row>
            </v-window-item>
            <v-window-item value="new-card" eager>
              <v-row class="mt-3">
                <v-col sm="6" offset-sm="3" lg="4" offset-lg="4">
                  <ac-stripe-charge @card="(card: StripeCardElement) => { stripeCard = card }" :key="clientSecret"/>
                </v-col>
                <v-col sm="3" offset-sm="3" lg="2" offset-lg="4" v-if="isRegistered && showSave">
                  <ac-bound-field
                      fieldType="ac-checkbox"
                      label="Save Card"
                      :field="ccForm.fields.save_card"
                  />
                </v-col>
                <v-col sm="3" lg="2" v-if="isRegistered && showSave">
                  <ac-bound-field
                      fieldType="ac-checkbox"
                      label="Make this my default card"
                      :field="ccForm.fields.make_primary"
                  />
                </v-col>
              </v-row>
              <slot name="new-card-button"/>
            </v-window-item>
          </v-window>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-else>
      <ac-loading-spinner/>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcSavedCardField from '@/components/fields/AcSavedCardField.vue'
import {flatten} from '@/lib/lib.ts'
import {getStripe} from '@/components/views/order/mixins/StripeMixin.ts'
import {StripeCardElement} from '@stripe/stripe-js'
import AcStripeCharge from '@/components/AcStripeCharge.vue'
import {mdiCreditCard, mdiContentSave} from '@mdi/js'
import {useList} from '@/store/lists/hooks.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {computed, ComputedRef, ref, watch} from 'vue'
import type {CreditCardToken, SubjectiveProps} from '@/types/main'
import {User} from '@/store/profiles/types/main'
import {RawData} from '@/store/forms/types/main'

declare type StripeError = { error: null | { message: string } }

declare interface AcCardManagerProps {
  ccForm: FormController,
  showSave?: boolean,
  saveOnly?: boolean,
  modelValue?: null | number,
  fieldMode?: boolean,
  clientSecret: string,
}

const props = withDefaults(defineProps<SubjectiveProps & AcCardManagerProps>(), {
  fieldMode: true,
  saveOnly: false,
  showSave: true,
  modelValue: null,
})
const emit = defineEmits<{ paymentSent: [], cardAdded: [], 'update:modelValue': [number | null] }>()

const setCard = (val: number | null) => {
  emit('update:modelValue', val)
}

const tab = ref('')
const lastCard = ref<null | number>(null)
const stripeCard = ref<StripeCardElement | null>(null)

let cardsName = `${flatten(props.username)}__creditCards`

const url = computed(() => `/api/sales/account/${props.username}/cards/`)

const {subject} = useSubject({ props })

// Should be set by the time we're here, and this will only be needed
// when dealing with registered users.
const viewerItems = useViewer()
const viewer = viewerItems.viewer as ComputedRef<User>
const {isRegistered} = viewerItems
const cards = useList<CreditCardToken>(cardsName, {
  endpoint: url.value,
  paginated: false,
  socketSettings: {
    appLabel: 'sales',
    modelName: 'CreditCardToken',
    serializer: 'CardSerializer',
    list: {
      appLabel: 'profiles',
      modelName: 'User',
      pk: viewer.value.id + '',
      listName: 'all_cards',
    },
  },
})

const initialize = () => {
  if (cards.list.length) {
    tab.value = 'saved-cards'
    const card = cards.list[0].x as CreditCardToken
    lastCard.value = card.id
    setCard(card.id)
  } else {
    tab.value = 'new-card'
    props.ccForm.fields.make_primary.update(true, false)
    // Should already be null, but just in case.
    setCard(null)
  }
}
cards.get().then(initialize)
watch(() => cards.list.length, initialize)

const handleStripeError = (result: StripeError) => {
  let message = result.error && result.error.message
  message = message || 'An unknown error occurred while trying to reach Stripe. Please contact support.'
  const ccForm = props.ccForm
  ccForm.errors = [message]
  ccForm.sending = false
}

const stripeSubmit = () => {
  const stripe = getStripe()
  const secret = props.clientSecret
  /* istanbul ignore if */
  if (!(stripe && secret)) {
    return
  }
  const ccForm = props.ccForm
  ccForm.sending = true
  if (props.saveOnly) {
    stripe.confirmCardSetup(
        secret,
        {
          payment_method: {
            card: stripeCard.value!,
            billing_details: {},
          },
        },
    ).then((response: StripeError | any) => {
      const result = response || {}
      ccForm.sending = false
      if (result.error) {
        handleStripeError(result)
        return
      }
      tab.value = 'saved-cards'
      emit('cardAdded')
    })
  } else {
    const data: RawData = {}
    if (tab.value === 'new-card') {
      data.payment_method = {card: stripeCard.value}
    }
    stripe.confirmCardPayment(
        secret,
        data,
    ).then((result: StripeError | any) => {
      if (result.error) {
        handleStripeError(result)
        ccForm.sending = false
        return
      }
      emit('paymentSent')
    })
  }
}

watch(() => props.username, () => {
  cards.endpoint = url.value
  // eslint-disable-next-line vue/no-mutating-props
  props.ccForm.endpoint = url.value
})

watch(tab, (val: string) => {
  /* istanbul ignore if */
  if (!val) {
    return
  }
  if (val === 'new-card') {
    lastCard.value = props.ccForm.fields.card_id.value
    props.ccForm.fields.card_id.update(null)
  }
  if (val === 'saved-cards') {
    props.ccForm.fields.card_id.update(lastCard.value)
  }
})

watch(() => props.modelValue, (value: null | number) => {
  if (value) {
    lastCard.value = value
  }
})

defineExpose({stripeSubmit})
</script>

<style scoped>

</style>
