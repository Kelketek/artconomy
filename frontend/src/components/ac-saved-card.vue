<template>
  <v-layout row wrap>
    <v-flex xs5 class="pt-1">
        <v-radio :disabled="changing"
                 :type="inputType"
                 :label="issuer.name + ' x' + card.last_four" :id="'saved_card_' + card.id"
                 name="card"
                 :value="card.id"
                 class="mr-1"
        />
    </v-flex>
    <v-flex xs7 text-xs-right>
        <v-btn small v-if="card.primary" color="success" size="sm" :disabled="changing">Primary Card</v-btn>
        <v-btn small v-else color="primary" size="sm" :disabled="changing" @click="makePrimary">Make Primary</v-btn>
        <v-btn small color="error" @click="deleteCard()" size="sm" :disabled="changing"><i class="fa fa-trash-o"></i></v-btn>
    </v-flex>
  </v-layout>
</template>

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
      postDelete () {
        let index = this.cards.indexOf(this.card)
        this.cards.splice(index, 1)
        if (this.value === this.card.id) {
          return this.$emit('input', null)
        }
      },
      deleteCard () {
        this.changing = true
        artCall(
          `/api/sales/v1/account/${this.user.username}/cards/${this.card.id}/`,
          'DELETE', {}, this.postDelete
        )
      },
      makePrimary () {
        this.changing = true
        artCall(
          `/api/sales/v1/account/${this.user.username}/cards/${this.card.id}/primary/`,
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
    created () {
      if (this.value === null && this.card.primary) {
        this.updateSelect()
      }
    },
    computed: {
      issuer () {
        return ISSUERS[this.card.card_type]
      }
    }
  }
</script>
