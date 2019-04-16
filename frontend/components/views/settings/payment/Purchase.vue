<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <v-layout id="purchase-settings" v-if="!(subject.landscape || subject.portrait)">
        <v-layout row wrap>
          <v-flex xs12 sm8 offset-sm2 md6 offset-md3 lg4 offset-lg4>
            <v-subheader>Saved Cards</v-subheader>
          </v-flex>
          <v-flex xs12 sm8 offset-sm2 md6 offset-md3 lg4 offset-lg4>
            <v-card>
              <v-card-text>
                <ac-card v-for="card in cards.list" :card="card" :key="card.id" :card-list="cards"></ac-card>
                <v-flex v-if="cards.empty" text-xs-center>
                  <p>Cards saved during purchase will be listed here for management.</p>
                </v-flex>
              </v-card-text>
            </v-card>
          </v-flex>
        </v-layout>
      </v-layout>
      <v-layout v-else row wrap>
        <v-flex xs12>
          <v-card>
            <v-card-text>
              <v-flex xs12 text-xs-center>
                <p><strong>Your default card will be charged for subscription services.</strong></p>
              </v-flex>
              <v-form @submit.prevent="ccForm.submitThen(addCard)">
                <ac-form-container v-bind="ccForm.bind">
                  <ac-card-manager :username="username" :cc-form="ccForm" :show-save="false" :field-mode="false" ref="cardManager">
                    <template v-slot:new-card-bottom>
                      <v-flex xs12 text-xs-center>
                        <v-btn color="primary" type="submit" class="add-card-button">Add Card</v-btn>
                      </v-flex>
                    </template>
                  </ac-card-manager>
                </ac-form-container>
              </v-form>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcCardManager from './AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema} from '@/lib'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({components: {AcLoadSection, AcFormContainer, AcCardManager, AcCard}})
export default class Purchase extends mixins(Subjective) {
  public cards: ListController<CreditCardToken> = null as unknown as ListController<CreditCardToken>
  public ccForm: FormController = null as unknown as FormController

  public get url() {
    return `/api/sales/v1/account/${this.username}/cards/`
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
    this.ccForm = this.$getForm(`${this.username}__cards__new`, baseCardSchema(this.url))
    this.cards = this.$getList(`${this.username}__creditCards`, {
      endpoint: this.url,
      paginated: false,
    })
  }
}
</script>
