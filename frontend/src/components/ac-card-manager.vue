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
            <form>
              <ac-form-container ref="newCardForm" :schema="newCardSchema" :model="newCardModel"
                                 :options="newCardOptions" :success="addCard"
                                 :url="`/api/sales/v1/${this.username}/cards/`"
              >
                <b-button type="submit" variant="primary" @click.prevent="$refs.newCardForm.submit">Add Card</b-button>
              </ac-form-container>
            </form>
          </b-tab>
        </b-tabs>
      </div>
    </div>
</template>

<script>
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  import Paginated from '../mixins/paginated'
  import AcFormContainer from './ac-form-container'
  import AcSavedCard from './ac-saved-card'
  import VueFormGenerator from 'vue-form-generator'
  import { artCall } from '../lib'
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
          card_number: '',
          exp_date: '',
          security_code: '',
          zip: ''
        },
        showNew: false,
        newCardSchema: {
          fields: [{
            type: 'input',
            inputType: 'text',
            label: 'Card Number',
            model: 'card_number',
            placeholder: '5555 5555 5555 5555',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.creditCard
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Expiration Date',
            model: 'exp_date',
            placeholder: '01/25',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'input',
            inputType: 'text',
            label: 'Security Code (CVV)',
            model: 'security_code',
            placeholder: '555',
            featured: true,
            required: true,
            hint: 'Three to four digit number, on the front of American Express cards, and on the back of all other cards.',
            validator: VueFormGenerator.validators.string
          },
          {
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
      addCard (response) {
        this.growing.push(response)
        this.currentTab = 0
        this.selectedCard = response.id
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
    created () {
      artCall(`/api/sales/v1/${this.username}/cards/`, 'GET', undefined, this.populateCards)
    }
  }
</script>