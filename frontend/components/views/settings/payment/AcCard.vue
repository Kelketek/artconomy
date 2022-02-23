<template>
  <v-col class="saved-card-container" cols="12" v-if="card.x">
    <v-row no-gutters  align="center">
      <v-col class="shrink px-2" v-if="fieldMode" >
        <v-radio :value="card.x.id" :disabled="wrongProcessor"></v-radio>
      </v-col>
      <v-col class="text-center fill-height shrink px-2" >
        <v-icon>{{cardIcon}}</v-icon>
      </v-col>
      <v-col class="text-center fill-height shrink px-2" >
        <v-row no-gutters justify="center" align="center">
          <v-col class="text-center" >x{{card.x.last_four}}</v-col>
        </v-row>
      </v-col>
      <v-col class="text-right fill-height grow" >
        <v-tooltip v-if="wrongProcessor" top>
          <template v-slot:activator="{on}">
            <v-btn color="yellow" v-on="on" icon small class="default-indicator"><v-icon>warning</v-icon></v-btn>
          </template>
          <span>
            Artconomy is transitioning processors. You may need to re-enter your card information to use this card.
          </span>
        </v-tooltip>
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
      </v-col>
    </v-row>
  </v-col>
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
import {artCall} from '@/lib/lib'

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

    @Prop({default: ''})
    public processor!: string

    public deleteCard() {
      this.card.delete().then(this.cardList.get)
    }

    public get wrongProcessor() {
      if (!this.processor || !this.card.x) {
        return false
      }
      return this.processor !== this.card.x.processor
    }

    public setPrimary() {
      this.cardList.list.map((card) => { // eslint-disable-line array-callback-return
        card.updateX({primary: false})
      })
      this.card.setX({...(this.card.x as CreditCardToken), ...{primary: true}})
    }

    public makePrimary() {
      artCall({url: `${this.card.endpoint}primary/`, method: 'post'}).then(this.setPrimary)
    }

    public get cardIcon() {
      if (!this.card.x) {
        return 'fa-credit-card-alt'
      }
      return typeMap[this.card.x.type]
    }
}
</script>
