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
            <v-tab href="#new-card" class="new-card-tab">
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
                  <ac-saved-card-field v-if="fieldMode" :model-value="modelValue" @input="setCard" :cards="cards"
                                       :processor="processor"/>
                  <ac-card v-else v-for="card in cards.list" :card="card" :key="card.x!.id" :card-list="cards"
                           :processor="processor"/>
                </v-col>
                <v-col cols="12" sm="8" offset-sm="2" md="6" offset-md="3" lg="4" offset-lg="4"
                       v-if="selectedCard && !selectedCard.cvv_verified">
                  <ac-bound-field
                      :field="ccForm.fields.cvv"
                      label="CVV"
                      :hint="hints.cvv"
                      class="cvv-verify"
                  />
                </v-col>
              </v-row>
            </v-window-item>
            <v-window-item value="new-card" eager>
              <v-row>
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

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {ListController} from '@/store/lists/controller.ts'
import {CreditCardToken} from '@/types/CreditCardToken.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {Countries} from '@/types/Countries.ts'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcSavedCardField from '@/components/fields/AcSavedCardField.vue'
import {cardHelperMap, flatten} from '@/lib/lib.ts'
import StripeMixin from '@/components/views/order/mixins/StripeMixin.ts'
import {StripeCardElement} from '@stripe/stripe-js'
import AcStripeCharge from '@/components/AcStripeCharge.vue'
import {RawData} from '@/store/forms/types/RawData.ts'
import {User} from '@/store/profiles/types/User.ts'
import {mdiCreditCard, mdiContentSave} from '@mdi/js'

declare type StripeError = { error: null | { message: string } }

@Component({
  components: {
    AcStripeCharge,
    AcSavedCardField,
    AcLoadSection,
    AcCard,
    AcBoundField,
    AcLoadingSpinner,
  },
  emits: ['paymentSent', 'cardAdded', 'update:modelValue'],
})
class AcCardManager extends mixins(Subjective, Alerts, StripeMixin) {
  public cards: ListController<CreditCardToken> = null as unknown as ListController<CreditCardToken>
  @Prop({required: true})
  public ccForm!: FormController

  @Prop({default: true})
  public showSave!: boolean

  public countries: SingleController<Countries> = null as unknown as SingleController<Countries>
  public tab: string = ''
  @Prop({default: true})
  public fieldMode!: boolean

  @Prop()
  public modelValue!: number | null

  @Prop()
  public clientSecret!: string

  @Prop({default: ''})
  public processor!: string

  @Prop({default: false})
  public showAll!: boolean

  @Prop({default: false})
  public saveOnly!: boolean

  public lastCard: null | number = null
  public stripeCard: StripeCardElement | null = null
  public mdiCreditCard = mdiCreditCard
  public mdiContentSave = mdiContentSave

  public created() {
    let cardsName = `${flatten(this.username)}__creditCards`
    let listName: string
    if (this.processor && !this.showAll) {
      cardsName += `__${this.processor}`
      listName = `${this.processor}_cards`
    } else {
      listName = 'all_cards'
    }
    // Should be set by the time we're here, and this will only be needed
    // when dealing with registered users.
    const viewer = this.viewer as User
    this.cards = this.$getList(cardsName, {
      endpoint: this.url,
      paginated: false,
      socketSettings: {
        appLabel: 'sales',
        modelName: 'CreditCardToken',
        serializer: 'CardSerializer',
        list: {
          appLabel: 'profiles',
          modelName: 'User',
          pk: viewer.id + '',
          listName,
        },
      },
    })
    this.cards.get().then(this.initialize)
  }

  public setCard(val: number | null) {
    this.$emit('update:modelValue', val)
  }

  @Watch('tab')
  public switchValues(val: string) {
    /* istanbul ignore if */
    if (!val) {
      return
    }
    if (val === 'new-card') {
      this.lastCard = this.ccForm.fields.card_id.value
      this.ccForm.fields.card_id.update(null)
    }
    if (val === 'saved-cards') {
      this.ccForm.fields.card_id.update(this.lastCard)
    }
  }

  @Watch('modelValue')
  public updateSaved(value: number | null) {
    if (value) {
      this.lastCard = value
    }
  }

  @Watch('username')
  public updateUrl() {
    this.cards.endpoint = this.url
    this.ccForm.endpoint = this.url
  }

  @Watch('cards.list.length')
  public initialize() {
    if (this.cards.list.length) {
      this.tab = 'saved-cards'
      const card = this.cards.list[0].x as CreditCardToken
      this.lastCard = card.id
      this.setCard(card.id)
    } else {
      this.tab = 'new-card'
      this.ccForm.fields.make_primary.update(true, false)
      // Should already be null, but just in case.
      this.setCard(null)
    }
  }

  public handleStripeError(result: StripeError) {
    let message = result.error && result.error.message
    message = message || 'An unknown error occurred while trying to reach Stripe. Please contact support.'
    this.ccForm.errors = [message]
    this.ccForm.sending = false
  }

  public stripeSubmit() {
    const stripe = this.stripe()
    const secret = this.clientSecret
    /* istanbul ignore if */
    if (!(stripe && secret)) {
      return
    }
    this.ccForm.sending = true
    if (this.saveOnly) {
      stripe.confirmCardSetup(
          secret,
          {
            payment_method: {
              card: this.stripeCard!,
              billing_details: {},
            },
          },
      ).then((response: StripeError | any) => {
        const result = response || {}
        this.ccForm.sending = false
        if (result.error) {
          this.handleStripeError(result)
          return
        }
        this.tab = 'saved-cards'
        this.$emit('cardAdded')
      })
    } else {
      const data: RawData = {}
      if (this.tab === 'new-card') {
        data.payment_method = {card: this.stripeCard}
      }
      stripe.confirmCardPayment(
          secret,
          data,
      ).then((result: StripeError | any) => {
        if (result.error) {
          this.handleStripeError(result)
          this.ccForm.sending = false
          return
        }
        this.$emit('paymentSent')
      })
    }
  }

  public get hints() {
    /* istanbul ignore if */
    if (!this.selectedCard) {
      return {cvv: ''}
    }
    return cardHelperMap[this.selectedCard.type] || cardHelperMap.default
  }

  public get selectedCard() {
    const value = this.ccForm.fields.card_id.value
    /* istanbul ignore if */
    if (!value) {
      return null
    }
    const selectedCard = this.cards.list.filter((card) => (card.x as CreditCardToken).id === value)[0]
    /* istanbul ignore if */
    if (!selectedCard) {
      return null
    }
    return selectedCard.x
  }

  public get url() {
    let url = `/api/sales/account/${this.username}/cards/`
    if (this.showAll) {
      return url
    }
    if (this.processor) {
      url += `${this.processor}/`
    }
    return url
  }
}

export default toNative(AcCardManager)
</script>

<style scoped>

</style>
