<template>
  <v-col class="saved-card-container" cols="12" v-if="card.x">
    <v-row no-gutters align="center">
      <v-col class="shrink px-2" v-if="fieldMode">
        <v-radio :value="card.x.id" :disabled="wrongProcessor"></v-radio>
      </v-col>
      <v-col class="text-center fill-height shrink px-2">
        <ac-icon :icon="cardIcon" v-if="cardIcon"/>
        <v-icon :icon="mdiCreditCard" v-else/>
      </v-col>
      <v-col class="text-center fill-height shrink px-2">
        <v-row no-gutters justify="center" align="center">
          <v-col class="text-center">x{{card.x!.last_four}}</v-col>
        </v-row>
      </v-col>
      <v-col class="text-right fill-height grow">
        <v-tooltip v-if="wrongProcessor" top>
          <template v-slot:activator="{props}">
            <v-btn color="yellow" v-bind="props" icon size="x-small" class="default-indicator">
              <v-icon :icon="mdiAlert" size="x-large"/>
            </v-btn>
          </template>
          <span>
            Artconomy is transitioning processors. You may need to re-enter your card information to use this card.
          </span>
        </v-tooltip>
        <v-tooltip v-if="card.x.primary" top>
          <template v-slot:activator="{props}">
            <v-btn color="green" v-bind="props" icon size="x-small" class="default-indicator">
              <v-icon :icon="mdiStar" size="x-large"/>
            </v-btn>
          </template>
          <span>Default Card</span>
        </v-tooltip>
        <v-tooltip v-else top>
          <template v-slot:activator="{props}">
            <v-btn v-bind="props" size="x-small" icon @click="makePrimary" color="black" class="make-default">
              <v-icon :icon="mdiStarOutline" size="x-large"/>
            </v-btn>
          </template>
          <span>Set Default</span>
        </v-tooltip>
        <ac-confirmation :action="deleteCard" card-class="delete-confirm">
          <template v-slot:default="{on}">
            <v-btn v-on="on" icon size="x-small" color="error" class="delete-card">
              <v-icon :icon="mdiDelete" size="x-large"/>
            </v-btn>
          </template>
        </ac-confirmation>
      </v-col>
    </v-row>
  </v-col>
</template>

<style>
.saved-card-container .v-radio {
  margin: 0; }
  .saved-card-container .v-radio .v-input--selection-controls__input {
    margin: 0; }

</style>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller.ts'
import {CreditCardToken} from '@/types/CreditCardToken.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {artCall} from '@/lib/lib.ts'
import AcIcon from '@/components/AcIcon.vue'
import {ISSUERS} from '@/components/views/settings/payment/issuers.ts'
import {mdiCreditCard, mdiAlert, mdiStar, mdiStarOutline, mdiDelete} from '@mdi/js'

@Component({
  components: {
    AcConfirmation,
    AcIcon,
  },
})
class AcCard extends Vue {
  @Prop({required: true})
  public card!: SingleController<CreditCardToken>

  @Prop({required: true})
  public cardList!: ListController<CreditCardToken>

  @Prop({default: false})
  public fieldMode!: boolean

  @Prop({default: ''})
  public processor!: string

  public mdiCreditCard = mdiCreditCard
  public mdiAlert = mdiAlert
  public mdiStar = mdiStar
  public mdiStarOutline = mdiStarOutline
  public mdiDelete = mdiDelete

  public async deleteCard() {
    return this.card.delete().then(this.cardList.get)
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
    artCall({
      url: `${this.card.endpoint}primary/`,
      method: 'post',
    }).then(this.setPrimary)
  }

  public get cardIcon() {
    if (!this.card.x) {
      return null
    }
    return ISSUERS[this.card.x.type].icon
  }
}

export default toNative(AcCard)
</script>
