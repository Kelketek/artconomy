<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <v-row no-gutters id="purchase-settings" v-if="!(subject.landscape || subject.portrait || subject.landscape_enabled || subject.portrait_enabled)">
        <v-row no-gutters  >
          <v-col cols="12" sm="8" offset-sm="2" md="6" offset-md="3" lg="4" offset-lg="4">
            <v-subheader>Saved Cards</v-subheader>
          </v-col>
          <v-col cols="12" sm="8" offset-sm="2" md="6" offset-md="3" lg="4" offset-lg="4">
            <v-card>
              <v-card-text>
                <template v-for="card in cards.list">
                  <ac-card :card="card" :key="card.x.id" :card-list="cards" :processor="processor" v-if="card.x" />
                </template>
                <v-col class="text-center" v-if="cards.empty" >
                  <p>Cards saved during purchase will be listed here for management.</p>
                </v-col>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-row>
      <v-row no-gutters v-else>
        <v-col cols="12">
          <v-card>
            <v-card-text>
              <v-col class="text-center" cols="12">
                <p><strong>Your default card will be charged for subscription services.</strong></p>
              </v-col>
              <ac-form @submit.prevent="ccForm.submitThen(addCard)">
                <ac-form-container v-bind="ccForm.bind">
                  <ac-card-manager :username="username" :cc-form="ccForm" :show-save="false" :field-mode="false" ref="cardManager" :show-all="true" :processor="processor">
                    <template v-slot:new-card-button>
                      <v-col class="text-center" cols="12" >
                        <v-btn color="primary" type="submit" class="add-card-button">Add Card</v-btn>
                      </v-col>
                    </template>
                  </ac-card-manager>
                </ac-form-container>
              </ac-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcCardManager from './AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema, flatten} from '@/lib/lib'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcForm from '@/components/wrappers/AcForm.vue'

@Component({components: {AcForm, AcLoadSection, AcFormContainer, AcCardManager, AcCard}})
export default class Purchase extends mixins(Subjective) {
  public cards: ListController<CreditCardToken> = null as unknown as ListController<CreditCardToken>
  public ccForm: FormController = null as unknown as FormController

  public get url() {
    return `/api/sales/v1/account/${this.username}/cards/`
  }

  public get processor() {
    return window.DEFAULT_CARD_PROCESSOR
  }

  @Watch('username')
  public updateUrl() {
    this.cards.endpoint = this.url
  }

  public mounted() {
    // Placing this here since the card manager should have an opportunity to do it first.
    this.cards.firstRun()
  }

  public addCard(card: CreditCardToken) {
    if (card.primary) {
      for (const oldCard of this.cards.list) {
        oldCard.updateX({primary: false})
      }
    }
    this.cards.push(card)
  }

  public created() {
    const schema = baseCardSchema(this.url)
    delete schema.fields.save_card
    this.ccForm = this.$getForm(flatten(`${flatten(this.username)}__cards__new`), baseCardSchema(this.url))
    this.cards = this.$getList(`${flatten(this.username)}__creditCards`, {
      endpoint: this.url,
      paginated: false,
    })
  }
}
</script>
