<template>
  <v-layout row wrap>
    <v-flex xs12 v-if="subject && cards.ready">
      <v-layout>
        <v-flex>
          <v-tabs v-if="cards.list.length" v-model="tab" fixed-tabs>
            <v-tab href="#saved-cards">
              <v-icon>save</v-icon> Saved Cards
            </v-tab>
            <v-tab href="#new-card">
              <v-icon>credit_card</v-icon> New Card
            </v-tab>
          </v-tabs>
        </v-flex>
      </v-layout>
      <v-layout>
        <v-flex xs12>
          <v-tabs-items v-model="tab">
            <v-tab-item value="saved-cards">
              <v-layout row wrap>
                <v-flex xs12 sm8 offset-sm2 md6 offset-md3 lg4 offset-lg4>
                  <ac-saved-card-field v-if="fieldMode" :value="value" @input="setCard" :cards="cards"></ac-saved-card-field>
                  <ac-card v-else v-for="card in cards.list" :card="card" :key="card.id" :card-list="cards"></ac-card>
                </v-flex>
                <v-flex xs12 sm8 offset-sm2 md6 offset-md3 lg4 offset-lg4 v-if="selectedCard && !selectedCard.cvv_verified">
                  <ac-bound-field
                          :field="ccForm.fields.cvv"
                          label="CVV"
                          :hint="hints.cvv"
                          class="cvv-verify"
                  ></ac-bound-field>
                </v-flex>
              </v-layout>
            </v-tab-item>
            <v-tab-item value="new-card">
              <ac-new-card :cc-form="ccForm" :username="username" :first-card="!cards.list.length" :show-save="showSave"></ac-new-card>
              <slot name="new-card-bottom"></slot>
            </v-tab-item>
          </v-tabs-items>
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex v-else><ac-loading-spinner></ac-loading-spinner></v-flex>
  </v-layout>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import {Prop, Watch} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts'
import AcBoundField from '@/components/fields/AcBoundField'
import {SingleController} from '@/store/singles/controller'
import {Countries} from '@/types/Countries'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcNewCard from '@/components/views/settings/payment/AcNewCard.vue'
import AcSavedCardField from '@/components/fields/AcSavedCardField.vue'
import {cardHelperMap} from '@/lib'

  @Component({
    components: {AcSavedCardField, AcNewCard, AcLoadSection, AcCard, AcBoundField, AcLoadingSpinner},
  })
export default class AcCardManager extends mixins(Subjective, Alerts) {
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
    public value!: number|null
    public lastCard: null|number = null

    public created() {
      this.cards = this.$getList(`${this.username}__creditCards`, {endpoint: this.url, paginated: false})
      this.cards.get().then(this.initialize)
      // @ts-ignore
      window.cardThing = this
    }

    public setCard(val: number|null) {
      this.$emit('input', val)
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

    @Watch('value')
    public updateSaved(value: number|null) {
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

    public get hints() {
      /* istanbul ignore if */
      if (!this.selectedCard) {
        return null
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
      return `/api/sales/v1/account/${this.username}/cards/`
    }
}
</script>

<style scoped>

</style>