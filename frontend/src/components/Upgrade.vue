<template>
  <v-container>
    <v-card color="grey darken-3">
      <v-card-text>
        <v-layout row wrap>
            <v-flex>
              <h1>Upgrade Your Account</h1>
              <span class="subheading">Check out our options below to enhance your art experience!</span>
            </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
    <v-tabs-items v-model="tab">
      <v-tab-item id="selection">
        <v-layout row wrap class="mt-3" v-if="pricing !== null && selection === null">
          <v-flex xs12 md5>
            <v-card style="height: 100%" class="service-container">
              <v-card-title>
                <v-flex text-xs-center><v-icon>portrait</v-icon>&nbsp;Artconomy Portrait</v-flex>
              </v-card-title>
              <v-card-text>
                <v-layout>
                  <v-list>
                    <v-list-tile>Receive Notifications when your favorite artists become available</v-list-tile>
                    <v-divider />
                    <v-list-tile>...for ${{pricing.portrait_price}}/Month!</v-list-tile>
                  </v-list>
                </v-layout>
              </v-card-text>
              <v-card-text class="card-bottom text-xs-center">
                <v-btn color="primary" v-if="!portrait" @click="selection='portrait'">Get Portrait!</v-btn>
                <v-btn v-else :to="{name: 'Settings', params: {username: viewer.username, tabName: 'portrait'}}">Manage Portrait</v-btn>
              </v-card-text>
            </v-card>
          </v-flex>
          <v-flex xs12 md5 offset-md2>
            <v-card style="height: 100%">
              <v-card-title text-xs-center>
                <v-flex text-xs-center><v-icon>landscape</v-icon>&nbsp;Artconomy Landscape</v-flex></v-card-title>
              <v-card-text class="mb-5">
                <v-layout fill-height>
                  <v-list two-line>
                    <v-list-tile>Receive Notifications when your favorite artists become available</v-list-tile>
                    <v-divider />
                    <v-list-tile>Drop the per-commission percent fee of {{pricing.standard_percentage}}% down to {{pricing.landscape_percentage}}%</v-list-tile>
                    <v-divider />
                    <v-list-tile>Drop the per-commission static fee of ${{pricing.standard_static}} down to ${{pricing.landscape_static}}</v-list-tile>
                    <v-divider />
                    <v-list-tile>Be the first to try new features</v-list-tile>
                    <v-divider />
                    <v-list-tile>...All for ${{pricing.landscape_price}}/Month!</v-list-tile>
                  </v-list>
                </v-layout>
              </v-card-text>
              <v-card-text class="card-bottom text-xs-center">
                <v-btn color="primary" v-if="!landscape" @click="selection='landscape'">Get Landscape!</v-btn>
                <v-btn v-else :to="{name: 'Settings', params: {username: viewer.username, tabName: 'landscape'}}">Manage Landscape</v-btn>
              </v-card-text>
            </v-card>
          </v-flex>
        </v-layout>
      </v-tab-item>
      <v-tab-item id="payment">
        <v-layout row wrap class="mt-3" v-if="selection !== null">
          <v-flex xs12>
            <ac-card-manager
                ref="cardManager"
                :payment="true"
                :username="viewer.username"
                v-model="selectedCard"
            />
          </v-flex>
          <v-flex xs12 text-xs-center class="mt-3 mb-3 pr-2 pl-2">
            <p><strong>Add a card or select a saved one on the left.</strong></p>
            <p>Once you've selected a card, you may click 'start service' to upgrade your account.
              Upgraded services, as with all use of Artconomy's services, are subject to the <router-link :to="{name: 'TermsOfService'}">Terms of Service.</router-link></p>
            <p>Artconomy is based in the United States of America</p>
          </v-flex>
          <v-flex xs12 class="pricing-container" text-xs-center>
            <strong>Monthly charge: ${{price}}</strong> <br />
            <div v-if="selectedCardModel && selectedCardModel.cvv_verified === false">
              <strong>Card Security code (CVV): </strong><v-text-field :autofocus="true" v-model="cvv" /> <br />
              <small>Three to four digit number, on the front of American Express cards, and on the back of all other cards.</small>
            </div>
            <div class="mt-2 text-xs-center">
              <v-btn @click="selection=null">Go back</v-btn>
              <ac-action class="pay-button" :disabled="selectedCard === null || !validCVV" :url="`${url}`" variant="success" :send="paymentData" :success="postPay">Start service</ac-action>
            </div>
          </v-flex>
        </v-layout>
      </v-tab-item>
      <v-tab-item id="completed">
        <v-flex xs12 text-xs-center class="mt-4">
          <i class="fa fa-5x fa-check-circle"></i><br />
          <p><strong>Your payment has been received!</strong></p>
          <p>We've received your payment and your account has been upgraded! Visit your <router-link :to="{name: 'Settings', params: {username: viewer.username}}">settings page</router-link> to view and manage your upgraded account settings.</p>
        </v-flex>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import {artCall, setCookie} from '../lib'
  import AcCardManager from './ac-card-manager'
  import AcAction from './ac-action'
  export default {
    name: 'Upgrade',
    components: {AcAction, AcCardManager},
    mixins: [Viewer],
    data () {
      return {
        pricing: null,
        selection: null,
        selectedCard: null,
        selectedCardModel: null,
        paid: false,
        cvv: '',
        url: '/api/sales/v1/premium/'
      }
    },
    methods: {
      loadPricing (response) {
        this.pricing = response
      },
      postPay (response) {
        this.paid = true
        this.$setUser(response.username, response)
        setCookie('csrftoken', response.csrftoken)
        setCookie('authtoken', response.authtoken)
        this.$root.$loadUser(false)
      }
    },
    created () {
      artCall('/api/sales/v1/pricing-info/', 'GET', undefined, this.loadPricing, this.$error)
    },
    computed: {
      tab () {
        if (this.selection === null) {
          return 'selection'
        } else if (this.paid) {
          return 'completed'
        } else {
          return 'payment'
        }
      },
      price () {
        return this.pricing[this.selection + '_price']
      },
      paymentData () {
        return {
          card_id: this.selectedCard,
          service: this.selection,
          cvv: this.cvv
        }
      },
      validCVV () {
        if (this.$refs.cardManager.selectedCardModel && this.$refs.cardManager.selectedCardModel.cvv_verified === true) {
          return true
        }
        return RegExp('^\\d{3,4}$').test(this.cvv)
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
  .card-bottom {
    position: absolute;
    bottom: 0;
    height: 75px;
  }
  .service-container {
    padding-bottom: 75px;
  }
</style>