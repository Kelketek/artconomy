<template>
  <v-container fluid grid-list-sm py-0>
    <v-flex xs12 sm8 offset-sm2 md6 offset-md3 lg4 offset-lg4>
      <v-subheader v-if="firstCard">New Card</v-subheader>
      <v-layout row wrap>
        <v-flex xs12 sm6>
          <ac-bound-field
              :field="ccForm.fields.first_name" label="First Name"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6>
          <ac-bound-field
              :field="ccForm.fields.last_name"
              label="Last Name"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs12 class="card-type-selector">
          <v-layout class="text-xs-center">
            <v-flex><v-icon :class="{picked: ccType === 'visa'}">fa-cc-visa</v-icon></v-flex>
            <v-flex><v-icon :class="{picked: ccType === 'mastercard'}">fa-cc-mastercard</v-icon></v-flex>
            <v-flex><v-icon :class="{picked: ccType === 'discover'}">fa-cc-discover</v-icon></v-flex>
            <v-flex><v-icon :class="{picked: ccType === 'amex'}">fa-cc-amex</v-icon></v-flex>
            <v-flex><v-icon :class="{picked: ccType === 'diners-club'}">fa-cc-diners-club</v-icon></v-flex>
          </v-layout>
        </v-flex>
        <v-flex xs8>
          <ac-bound-field
              :field="ccForm.fields.number"
              label="Card Number"
              placeholder="#### #### #### ####"
              :mask="hints.mask"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs4>
          <ac-bound-field
              :field="ccForm.fields.cvv"
              label="CVV"
              :hint="hints.cvv"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs6>
          <ac-bound-field
              :field="ccForm.fields.exp_date"
              label="Exp Date"
              mask="##/##"
              placeholder="MM/YY"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs6>
          <ac-bound-field
              :field="ccForm.fields.zip"
              label="Zip/Postal Code"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs12>
          <ac-bound-field fieldType="v-autocomplete" :field="ccForm.fields.country" :items="countryOptions">
          </ac-bound-field>
        </v-flex>
        <v-flex xs12 sm6 v-if="isRegistered && showSave">
          <ac-bound-field
              fieldType="v-checkbox"
              label="Save Card"
              :field="ccForm.fields.save_card"
          ></ac-bound-field>
        </v-flex>
        <v-flex xs12 :class="{sm6: showSave}" v-if="!firstCard && isRegistered">
          <ac-bound-field
              fieldType="v-checkbox"
              label="Make this my default card"
              :field="ccForm.fields.make_primary"
          ></ac-bound-field>
        </v-flex>
      </v-layout>
    </v-flex>
  </v-container>
</template>

<!--suppress CssUnusedSymbol -->
<style scoped>
  .card-type-selector .fa{
    opacity: .5;
  }

  .card-type-selector .fa.picked {
    opacity: 1;
  }
</style>

<script lang="ts">
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {FormController} from '@/store/forms/form-controller'
import {SingleController} from '@/store/singles/controller'
import {Countries} from '@/types/Countries'
import {SelectOption} from '@/store/forms/types/SelectOption'
import {Prop} from 'vue-property-decorator'
import Component, {mixins} from 'vue-class-component'
import {cardType, CardType} from '@/store/forms/validators'
import Viewer from '@/mixins/viewer'
import {cardHelperMap} from '@/lib'

@Component({components: {AcBoundField, AcFormContainer}})
export default class AcNewCard extends mixins(Viewer) {
  @Prop({default: false})
  public firstCard!: boolean
  @Prop({default: true})
  public showSave!: boolean
  @Prop({required: true})
  public ccForm!: FormController
  public countries: SingleController<Countries> = null as unknown as SingleController<Countries>

  public get countryOptions() {
    let options: SelectOption[] = []
    if (this.countries.x) {
      const countries = this.countries.x as Countries
      options = Object.keys(countries).map((key) => ({value: key, text: countries[key]}))
    }
    return options
  }

  public get ccType(): CardType {
    return cardType(this.ccForm.fields.number.value)
  }

  public get hints() {
    return cardHelperMap[this.ccType] || cardHelperMap.default
  }

  public created() {
    this.countries = this.$getSingle('countries', {persist: true, endpoint: '/api/lib/v1/countries/'})
    this.countries.get().then()
  }
}
</script>
