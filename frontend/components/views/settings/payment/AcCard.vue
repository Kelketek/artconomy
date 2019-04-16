<template>
  <v-flex xs12 saved-card-container>
    <v-layout row align-center>
      <v-flex v-if="fieldMode" shrink px-2>
        <v-radio :value="card.x.id"></v-radio>
      </v-flex>
      <v-flex text-xs-center fill-height shrink px-2>
        <v-icon>{{cardIcon}}</v-icon>
      </v-flex>
      <v-flex text-xs-center fill-height shrink px-2>
        <v-layout justify-center align-center>
          <v-flex text-xs-center>x{{card.x.last_four}}</v-flex>
        </v-layout>
      </v-flex>
      <v-flex text-xs-right fill-height grow>
        <v-tooltip v-if="card.x.primary" top>
          <template v-slot:activator="{on}">
            <v-btn color="green" v-on="on" icon small class="default-indicator"><v-icon>star</v-icon></v-btn>
          </template>
          <span>Default Card</span>
        </v-tooltip>
        <v-tooltip v-else top>
          <template v-slot:activator="{on}">
            <v-btn v-on="on" small icon @click="makePrimary" color="black" class="make-default"><v-icon>star_border</v-icon></v-btn>
          </template>
          <span>Set Default</span>
        </v-tooltip>
        <ac-confirmation :action="deleteCard" card-class="delete-confirm">
          <template v-slot:default="{on}">
            <v-btn v-on="on" icon small color="error" class="delete-card"><v-icon>delete</v-icon></v-btn>
          </template>
        </ac-confirmation>
      </v-flex>
    </v-layout>
  </v-flex>
</template>

<style lang="sass">
  .saved-card-container
    .v-radio
      margin: 0
      .v-input--selection-controls__input
        margin: 0
</style>

<script lang="ts">
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import Component from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import {CreditCardToken} from '@/types/CreditCardToken'
import {ListController} from '@/store/lists/controller'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {artCall} from '@/lib'

const typeMap: {[key: number]: string} = {
  1: 'fa-cc-visa',
  2: 'fa-cc-mastercard',
  3: 'fa-cc-amex',
  4: 'fa-cc-discover',
  5: 'fa-cc-diners-club',
}
  @Component({
    components: {AcConfirmation},
  })
export default class AcCard extends Vue {
    @Prop({required: true})
    public card!: SingleController<CreditCardToken>

    @Prop({required: true})
    public cardList!: ListController<CreditCardToken>

    @Prop({default: false})
    public fieldMode!: boolean

    public deleteCard() {
      this.card.delete().then(this.cardList.get)
    }

    public setPrimary() {
      this.cardList.list.map((card) => {
        card.updateX({primary: false})
      })
      this.card.setX({...(this.card.x as CreditCardToken), ...{primary: true}})
    }

    public makePrimary() {
      artCall({url: `${this.card.endpoint}primary/`, method: 'post'}).then(this.setPrimary)
    }

    public get cardIcon() {
      const card = this.card.x as CreditCardToken
      return typeMap[card.type]
    }
}
</script>
