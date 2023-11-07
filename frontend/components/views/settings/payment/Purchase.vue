<template>
  <ac-load-section :controller="subjectHandler.user">
    <template v-slot:default>
      <v-row no-gutters>
        <v-col cols="12">
          <v-card>
            <v-card-text>
              <v-col class="text-center" cols="12">
                <p><strong>Your default card will be charged for subscription services.</strong></p>
              </v-col>
              <ac-load-section :controller="clientSecret">
                <template v-slot:default>
                  <ac-form @submit.prevent="submitNewCard">
                    <ac-form-container v-bind="ccForm.bind">
                      <ac-card-manager
                          :username="username"
                          :cc-form="ccForm"
                          :show-save="false"
                          :field-mode="false"
                          ref="cardManager"
                          :show-all="true"
                          :processor="processor"
                          :save-only="true"
                          @cardAdded="fetchSecret"
                          :client-secret="(clientSecret.x && clientSecret.x.secret) || ''"
                      >
                        <template v-slot:new-card-button>
                          <v-col class="text-center" cols="12">
                            <v-btn color="primary" type="submit" class="add-card-button" variant="flat">Add Card</v-btn>
                          </v-col>
                        </template>
                      </ac-card-manager>
                    </ac-form-container>
                  </ac-form>
                </template>
              </ac-load-section>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective'
import AcCardManager from './AcCardManager.vue'
import {FormController} from '@/store/forms/form-controller'
import {baseCardSchema, flatten} from '@/lib/lib'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {ListController} from '@/store/lists/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import AcCard from '@/components/views/settings/payment/AcCard.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import {SingleController} from '@/store/singles/controller'
import ClientSecret from '@/types/ClientSecret'
import {User} from '@/store/profiles/types/User'

@Component({
  components: {
    AcForm,
    AcLoadSection,
    AcFormContainer,
    AcCardManager,
    AcCard,
  },
})
class Purchase extends mixins(Subjective) {
  public cards: ListController<CreditCardToken> = null as unknown as ListController<CreditCardToken>
  public ccForm: FormController = null as unknown as FormController
  public clientSecret = null as unknown as SingleController<ClientSecret>

  public get url() {
    return `/api/sales/account/${this.username}/cards/`
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

  public submitNewCard() {
    if (this.processor === 'authorize') {
      this.ccForm.submitThen(this.addCard)
      return
    }
    // @ts-ignore
    this.$refs.cardManager.stripeSubmit()
  }

  public fetchSecret() {
    this.clientSecret.fetching = true
    this.clientSecret.post().then(this.clientSecret.makeReady)
  }

  public created() {
    const schema = baseCardSchema(this.url)
    delete schema.fields.save_card
    this.clientSecret = this.$getSingle(
        `${flatten(this.username)}__new_card__clientSecret`, {
          endpoint: `/api/sales/account/${this.username}/cards/setup-intent/`,
        })
    this.fetchSecret()
    this.ccForm = this.$getForm(flatten(`${flatten(this.username)}__cards__new`), baseCardSchema(this.url))
    const viewer = this.viewer as User
    this.cards = this.$getList(`${flatten(this.username)}__creditCards`, {
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
          listName: 'all_cards',
        },
      },
    })
  }
}

export default toNative(Purchase)
</script>
