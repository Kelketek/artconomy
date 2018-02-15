<template>
  <div class="card-manager">
      <div class="card">
        <b-tabs card v-model="currentTab">
          <b-tab title="Saved Cards">
              <div class="card-body">
                <ac-saved-card
                    v-for="card in growing"
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
              </div>
          </b-tab>
          <b-tab title="New Card">
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
                                 :url="`/api/sales/v1/${this.username}/cards/`"
              >
                <v-btn type="submit" color="primary" @click.prevent="$refs.newCardForm.submit">Add Card</v-btn>
              </ac-form-container>
            </form>
          </b-tab>
        </b-tabs>
      </div>
    </div>
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
        currentTab: 0,
        selectedCard: this.value,
        newCardModel: {
          first_name: '',
          last_name: '',
          country: 'US',
          card_number: '',
          exp_date: '',
          security_code: '',
          zip: ''
        },
        showNew: false,
        cardType: 'unknown',
        newCardSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'First Name',
            model: 'first_name',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          },
          {
            type: 'input',
            inputType: 'text',
            label: 'Last Name',
            model: 'last_name',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Card Number',
            model: 'card_number',
            placeholder: '5555 5555 5555 5555',
            featured: true,
            required: true,
            validator: cardSelectValidator
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Expiration Date',
            model: 'exp_date',
            placeholder: 'MM/YY',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'select',
            model: 'country',
            values: [],
            required: true,
            label: 'Country',
            selectOptions: {
              hideNoneSelectedText: true
            }
          }, {
            type: 'input',
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
          this.currentTab = 1
        }
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
        this.currentTab = 0
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
      selectedCard (newValue) {
        if (newValue === null) {
          if (this.growing.length === 0) {
            this.currentTab = 1
          } else {
            this.selectedCard = this.growing[0].id
          }
        }
        this.$emit('input', this.selectedCard)
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
      artCall(`/api/sales/v1/${this.username}/cards/`, 'GET', undefined, this.populateCards)
      artCall('/api/lib/v1/countries/', 'GET', undefined, this.populateCountries)
      EventBus.$on('card-number', this.selectCard)
    },
    destroyed () {
      EventBus.$off('card-number', this.selectCard)
    }
  }
</script>