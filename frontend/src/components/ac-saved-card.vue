<template>
  <div class="saved-card">
    <div class="credit-card-info">
      <input :disabled="changing" :type="inputType" :id="'saved_card_' + card.id" name="card" :value="card.id" :checked="card.id === value" class="mr-1" @input="updateSelect()"/>
      <label :for="'saved_card' + card.id"><i class="fa" :class="class_obj()"></i> {{ issuer.name }} x{{ card.last_four }}</label>
    </div>
    <div class="credit-card-buttons">
      <b-button v-if="card.primary" variant="success" size="sm" :disabled="changing">Primary Card</b-button>
      <b-button v-else variant="primary" size="sm" :disabled="changing" @click="makePrimary">Make Primary</b-button>
      <b-button variant="danger" @click="deleteCard()" size="sm" :disabled="changing"><i class="fa fa-trash-o"></i></b-button>
    </div>
    <div class="clear"></div>
    <div class="mb-2"></div>
  </div>
</template>

<style scoped>
  .credit-card-info {
    display: block;
    float: left;
  }
  .credit-card-buttons {
    display: block;
    float: right;
  }
  .clear {
    clear: both;
  }
</style>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { artCall } from '../lib'

  const ISSUERS = {
    1: {'name': 'Visa', 'icon': 'fa-cc-visa'},
    2: {'name': 'Mastercard', 'icon': 'fa-cc-mastercard'},
    3: {'name': 'American Express', 'icon': 'fa-cc-amex'},
    4: {'name': 'Discover', 'icon': 'fa-cc-discover'},
    5: {'name': "Diner's Club", 'icon': 'fa-cc-diners-club'}
  }
  export default {
    name: 'ac-saved-card',
    props: ['cards', 'value', 'card', 'selectable'],
    mixins: [Viewer, Perms],
    methods: {
      class_obj () {
        let key = this.issuer.icon
        let result = {'fa-lg': true}
        result[key] = true
        return result
      },
      updateSelect () {
        return this.$emit('input', this.card.id)
      },
      postDelete () {
        let index = this.cards.indexOf(this.card)
        this.cards.splice(index, 1)
      },
      deleteCard () {
        this.changing = true
        artCall(
          `/api/sales/v1/${this.user.username}/cards/${this.card.id}/`,
          'DELETE', {}, this.postDelete
        )
      },
      makePrimary () {
        this.changing = true
        artCall(
          `/api/sales/v1/${this.user.username}/cards/${this.card.id}/primary/`,
          'POST', {}, this.postPrimary
        )
      },
      postPrimary () {
        for (let card in this.cards) {
          if (!this.cards.hasOwnProperty(card)) {
            continue
          }
          this.cards[card].primary = false
        }
        this.card.primary = true
        this.changing = false
        this.updateSelect()
      }

    },
    data: function () {
      return {
        changing: false,
        inputType: this.selectable ? 'radio' : 'hidden'
      }
    },
    computed: {
      'issuer': function () {
        return ISSUERS[this.card.card_type]
      }
    }
  }
</script>
