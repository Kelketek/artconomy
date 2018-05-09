<template>
  <v-card class="card-manager pr-2 pl-2">
    <v-tabs card v-model="currentTab">
      <v-tab href="#tab-saved-card">
        <v-icon>save</v-icon>&nbsp;Saved Cards
      </v-tab>
      <v-tab href="#tab-new-card">
        <v-icon>credit_card</v-icon>&nbsp;New Card
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="currentTab">
      <v-tab-item id="tab-saved-card">
        <v-radio-group v-model="selectedCard">
          <template v-for="(card, index) in growing">
            <ac-saved-card
                :key="card.id"
                v-if="growing !== null"
                :card="card"
                :cards="growing"
                :username="user.username"
                :selectable="payment"
                v-model="selectedCard"
            >
              {{card}}
            </ac-saved-card>
            <v-divider v-if="index + 1 < growing.length" :key="index" />
          </template>
        </v-radio-group>
      </v-tab-item>
      <v-tab-item id="tab-new-card" class="pt-2 pl-2 pb-2 pr-2">
        <form autocomplete="off">
          <div class="card-type-selector text-xs-center">
            <i class="fa fa-2x fa-cc-visa" :class="{picked: cardSelected('visa')}"></i>
            <i class="fa fa-2x fa-cc-mastercard" :class="{picked: cardSelected('mastercard')}"></i>
            <i class="fa fa-2x fa-cc-discover" :class="{picked: cardSelected('discover')}"></i>
            <i class="fa fa-2x fa-cc-amex" :class="{picked: cardSelected('amex')}"></i>
            <i class="fa fa-2x fa-cc-diners-club" :class="{picked: cardSelected('diners-club')}"></i>
          </div>
          <ac-form-container ref="newCardForm" :schema="newCardSchema" :model="newCardModel"
                             :options="newCardOptions" :success="addCard"
                             :url="`/api/sales/v1/account/${this.username}/cards/`"
          >
            <v-btn type="submit" color="primary" @click.prevent="$refs.newCardForm.submit">Add Card</v-btn>
          </ac-form-container>
        </form>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<style scoped>
  .card-type-selector .fa {
    opacity: .5;
  }
  .card-type-selector .fa.picked {
    opacity: 1;
  }
</style>

<script>
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  import Paginated from '../mixins/paginated'
  import AcFormContainer from './ac-form-container'
  import AcSavedCard from './ac-saved-card'
  import VueFormGenerator from 'vue-form-generator'
  import { artCall, EventBus, genOptions } from '../lib'

  function validCVV (value) {
    if (RegExp('^\\d{3,4}$').test(value)) {
      return
    }
    return ['Invalid CVV. Please check your card.']
  }

  function cardSelectValidator (value, field) {
    EventBus.$emit('card-number', value)
    return VueFormGenerator.validators.creditCard(value, field)
  }

  export default {
    name: 'ac-card-manager',
    props: ['username', 'payment', 'value'],
    mixins: [Viewer, Perms, Paginated],
    components: {AcFormContainer, AcSavedCard},
    data () {
      return {
        currentTab: 'tab-saved-card',
        selectedCard: this.value,
        newCardModel: {
          first_name: '',
          last_name: '',
          country: 'US',
          card_number: '',
          exp_date: '',
          security_code: '',
          zip: '',
          cvv: ''
        },
        showNew: false,
        cardType: 'unknown',
        newCardSchema: {
          fields: [{
            type: 'v-text',
            inputType: 'text',
            label: 'First Name',
            model: 'first_name',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'v-text',
            inputType: 'text',
            label: 'Last Name',
            model: 'last_name',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Card Number',
            model: 'card_number',
            placeholder: '5555 5555 5555 5555',
            mask: '#### - #### - #### - ####',
            featured: true,
            required: true,
            validator: cardSelectValidator
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'CVV',
            model: 'cvv',
            placeholder: 'XXX',
            hint: 'Three digit number on the back of most cards, four digit number on the front of American Express',
            featured: true,
            required: true,
            validator: validCVV
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Expiration Date',
            model: 'exp_date',
            placeholder: 'MM/YY',
            mask: '##/##',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-select',
            model: 'country',
            values: [],
            required: true,
            label: 'Country',
            selectOptions: {
              hideNoneSelectedText: true
            }
          }, {
            type: 'v-text',
            inputType: 'text',
            label: 'Zip/Postal Code',
            model: 'zip',
            placeholder: '55555',
            featured: true,
            validator: VueFormGenerator.validators.string
          }]
        },
        newCardOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      populateCards (response) {
        this.response = response
        this.growing = response.results
        if (this.growing.length === 0) {
          return
        }
        for (let card of this.growing) {
          if (card.primary) {
            this.selectedCard = card.id
            return
          }
        }
        this.selectedCard = this.growing[0].id
      },
      cardSelected (value) {
        return value === this.cardType
      },
      selectCard (value) {
        // start without knowing the credit card type
        let result = 'unknown'
        // first check for MasterCard
        if (/^5[1-5]/.test(value)) {
          result = 'mastercard'
        } else if (/^4/.test(value)) {
          result = 'visa'
        } else if (/^3[47]/.test(value)) {
          result = 'amex'
        } else if (/^6011/.test(value)) {
          result = 'discover'
        } else if (/^30[1-5]/.test(value)) {
          result = 'diners'
        }
        this.cardType = result
      },
      addCard (response) {
        this.growing.push(response)
        this.selectedCard = response.id
      },
      populateCountries (response) {
        let countryField = this.newCardSchema.fields.filter((field) => { return field.model === 'country' })[0]
        countryField.values = () => {
          return genOptions(response)
        }
      }
    },
    watch: {
      selectedCard (newValue, oldValue) {
        this.$emit('input', newValue)
        this.currentTab = 'tab-saved-card'
      },
      currentTab (newValue) {
        if (newValue === 'tab-new-card') {
          this.$emit('input', null)
        } else {
          this.$emit('input', this.selectedCard)
        }
      },
      growing (newValue) {
        if (newValue.length === 0) {
          this.currentTab = 'tab-new-card'
        }
      }
    },
    computed: {
      selectedCardModel () {
        if (!this.selectedCard) {
          return null
        }
        return this.growing.filter((card) => { return card.id === this.selectedCard })[0]
      }
    },
    created () {
      artCall(`/api/sales/v1/account/${this.username}/cards/`, 'GET', undefined, this.populateCards)
      artCall('/api/lib/v1/countries/', 'GET', undefined, this.populateCountries)
      EventBus.$on('card-number', this.selectCard)
    },
    destroyed () {
      EventBus.$off('card-number', this.selectCard)
    }
  }
</script>