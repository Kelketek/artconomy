<template>
  <v-container v-if="transfer">
    <v-card elevation-1>
      <v-layout row wrap>
        <v-flex xs12 md6 lg4 class="text-xs-center pr-1 pl-2 pt-1">
          <router-link
              :to="characterPath"
              v-if="transfer.character"
          >
             <ac-asset :asset="transfer.character.primary_asset" thumb-name="thumbnail" img-class="bound-image" />
          </router-link>
          <ac-asset v-else :asset="null"></ac-asset>
        </v-flex>
        <v-flex xs12 md6 lg8 class="text-xs-center pt-3 pl-2">
          <v-layout>
            <v-flex>
              <h1>Transferring <router-link :to="characterPath" v-if="transfer.character">{{characterName}}</router-link><span v-else>{{characterName}}</span></h1>
            </v-flex>
          </v-layout>
          <v-layout row wrap>
            <v-flex xs6>
              <strong>From</strong><br />
              <ac-avatar :user="transfer.seller" />
            </v-flex>
            <v-flex xs6>
              <strong>To</strong><br />
              <ac-avatar :user="transfer.buyer" />
            </v-flex>
            <v-flex xs12>
              <p v-if="cancelled"><strong>Transfer was cancelled.</strong></p>
              <p v-if="declined"><strong>Transfer was declined.</strong></p>
              <p v-if="completed"><strong>Transfer completed successfully.</strong></p>
              <p v-if="!price">There <span v-if="newTransfer">is</span><span v-else>was</span> no cost for this transfer.</p>
              <p v-else>Transfer price<span v-if="!newTransfer"> was</span>: ${{price}}</p>
            </v-flex>
            <v-flex xs12 v-if="isBuyer && newTransfer && price">
              <ac-card-manager
                  ref="cardManager"
                  :payment="true"
                  :username="transfer.buyer.username"
                  v-model="selectedCard"
              />
            </v-flex>
            <v-flex xs12 md6 text-xs-center class="mt-3 mb-3 pr-2 pl-2" v-if="isBuyer && newTransfer && price">
              <p><strong>Add a card or select a saved one on the left.</strong></p>
              <p>Once you've selected a card, you may click the pay button below to pay for the transfer.
                By paying, you are agreeing to the <router-link :to="{name: 'CharacterTransferAgreement'}">Character Transfer Agreement.</router-link></p>
              <p>Artconomy is based in the United States of America</p>
              <div class="pricing-container" :class="{'text-xs-center': isBuyer && newTransfer}">
                <strong>Total: ${{price}}</strong> <br />
                <div v-if="selectedCardModel && selectedCardModel.cvv_verified === false">
                  <strong>Card Security code (CVV): </strong><v-text-field :autofocus="true" v-model="cvv" /> <br />
                  <small>Three to four digit number, on the front of American Express cards, and on the back of all other cards.</small>
                </div>
                <div class="mt-2 text-xs-center">
                  <ac-action class="cancel-button" :url="`${url}cancel/`" color="red">Decline</ac-action>
                  <ac-action
                      class="pay-button" :disabled="selectedCard === null || !validCVV" :url="`${url}pay/`"
                      variant="success" :send="paymentData" :success="postPay" :confirm="true"
                  >
                    Submit
                    <div class="text-left" slot="confirmation-text">
                      <p>
                        I accept the
                        <router-link :to="{name: 'CharacterTransferAgreement'}">Character Transfer Agreement</router-link>
                        and accept that there are <strong>NO REFUNDS</strong> for character transfers.
                      </p>
                    </div>
                  </ac-action>
                </div>
              </div>
            </v-flex>
            <v-flex v-else-if="isBuyer && newTransfer" text-xs-center>
              <v-layout row>
                <v-flex xs6>
                  <ac-action class="cancel-button" :url="`${url}cancel/`" color="red" :success="setTransfer">Decline</ac-action>
                </v-flex>
                <v-flex xs6>
                  <ac-action class="pay-button" :url="`${url}pay/`" variant="success" :send="paymentData" :success="postPay" :confirm="true">
                    Accept
                    <div class="text-left" slot="confirmation-text">
                      <p>
                        I accept the
                        <router-link :to="{name: 'CharacterTransferAgreement'}">Character Transfer Agreement</router-link>
                        and understand that character transfers are final.
                      </p>
                    </div>
                  </ac-action>
                </v-flex>
              </v-layout>
            </v-flex>
            <v-flex v-else-if="isSeller && newTransfer" text-xs-center>
              <ac-action class="cancel-button" :url="`${url}cancel/`" color="red" :success="setTransfer">Decline</ac-action>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-layout>
    </v-card>
    <v-card v-if="transfer.include_assets && newTransfer" class="mt-2">
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>Included Assets</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <v-layout row wrap v-if="transfer.include_assets && newTransfer">
      <ac-asset-gallery
          :endpoint="`/api/sales/v1/transfer/character/${transferID}/assets/`"
      />
    </v-layout>
  </v-container>
</template>

<script>
  import {artCall} from '../lib'
  import AcAsset from './ac-asset'
  import AcAvatar from './ac-avatar'
  import AcAssetGallery from './ac-asset-gallery'
  import AcCardManager from './ac-card-manager'
  import Viewer from '../mixins/viewer'
  import AcAction from './ac-action'

  export default {
    name: 'CharacterTransfer',
    components: {AcAction, AcCardManager, AcAssetGallery, AcAvatar, AcAsset},
    mixins: [Viewer],
    props: ['transferID'],
    data () {
      return {
        transfer: null,
        selectedCard: null,
        selectedCardModel: null,
        cvv: '',
        url: `/api/sales/v1/transfer/character/${this.transferID}/`
      }
    },
    methods: {
      setTransfer (response) {
        this.transfer = response
      },
      postPay (response) {
        this.$router.history.push({name: 'Character', params: {username: response.buyer.username, characterName: response.character.name}})
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.setTransfer, this.$error)
    },
    computed: {
      characterName () {
        if (this.transfer.character) {
          return this.transfer.character.name
        } else {
          return '<<Unknown>>'
        }
      },
      characterPath () {
        return {name: 'Character', params: {username: this.transfer.character.user.username, characterName: this.transfer.character.name}}
      },
      price () {
        return parseFloat(this.transfer.price)
      },
      isBuyer () {
        return this.viewer.username === this.transfer.buyer.username
      },
      isSeller () {
        return this.viewer.username === this.transfer.seller.username
      },
      newTransfer () {
        return this.transfer.status === 0
      },
      completed () {
        return this.transfer.status === 1
      },
      cancelled () {
        return this.transfer.status === 2
      },
      declined () {
        return this.transfer.status === 3
      },
      validCVV () {
        if (this.$refs.cardManager.selectedCardModel && this.$refs.cardManager.selectedCardModel.cvv_verified === true) {
          return true
        }
        return RegExp('^\\d{3,4}$').test(this.cvv)
      },
      paymentData () {
        return {
          card_id: this.selectedCard,
          amount: this.transfer.price,
          cvv: this.cvv
        }
      }
    },
    watch: {
      selectedCard () {
        this.selectedCardModel = this.$refs.cardManager.selectedCardModel
      }
    }
  }
</script>

<style scoped>

</style>