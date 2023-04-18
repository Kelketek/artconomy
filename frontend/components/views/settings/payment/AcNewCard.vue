<template>
  <v-container class="py-0" fluid>
    <v-row no-gutters>
      <v-col cols="12" sm="8" offset-sm="2" md="6" offset-md="3" lg="4" offset-lg="4">
        <v-subheader v-if="firstCard">New Card</v-subheader>
        <v-row no-gutters  >
          <v-col cols="12" sm="6">
            <ac-bound-field
              :field="ccForm.fields.first_name" label="First Name"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <ac-bound-field
              :field="ccForm.fields.last_name"
              label="Last Name"
            />
          </v-col>
          <v-col cols="12" class="card-type-selector">
            <v-row no-gutters class="text-center">
              <v-col><v-icon :class="{picked: ccType === 'visa'}">fa-cc-visa</v-icon></v-col>
              <v-col><v-icon :class="{picked: ccType === 'mastercard'}">fa-cc-mastercard</v-icon></v-col>
              <v-col><v-icon :class="{picked: ccType === 'discover'}">fa-cc-discover</v-icon></v-col>
              <v-col><v-icon :class="{picked: ccType === 'amex'}">fa-cc-amex</v-icon></v-col>
              <v-col><v-icon :class="{picked: ccType === 'diners-club'}">fa-cc-diners-club</v-icon></v-col>
            </v-row>
          </v-col>
          <v-col cols="8">
            <ac-bound-field
              :field="ccForm.fields.number"
              label="Card Number"
              placeholder="#### #### #### ####"
              v-mask="hints.mask"
            />
          </v-col>
          <v-col cols="4">
            <ac-bound-field
              :field="ccForm.fields.cvv"
              label="CVV"
              :hint="hints.cvv"
            />
          </v-col>
          <v-col cols="6">
            <ac-bound-field
              :field="ccForm.fields.exp_date"
              label="Exp Date"
              v-mask="'##/####'"
              placeholder="MM/YY"
            />
          </v-col>
          <v-col cols="6">
            <ac-bound-field
              :field="ccForm.fields.zip"
              label="Zip/Postal Code"
            />
          </v-col>
          <v-col cols="12">
            <ac-bound-field fieldType="v-autocomplete" :field="ccForm.fields.country" :items="countryOptions">
            </ac-bound-field>
          </v-col>
          <v-col cols="12" sm="6" v-if="isRegistered && showSave">
            <ac-bound-field
              fieldType="ac-checkbox"
              label="Save Card"
              :field="ccForm.fields.save_card"
            />
          </v-col>
          <v-col cols="12" :class="{sm6: showSave}" v-if="!firstCard && isRegistered">
            <ac-bound-field
              fieldType="ac-checkbox"
              label="Make this my default card"
              :field="ccForm.fields.make_primary"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
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
import {cardHelperMap} from '@/lib/lib'
import {mask} from 'vue-the-mask'

@Component({components: {AcBoundField, AcFormContainer}, directives: {mask}})
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
    this.countries = this.$getSingle('countries', {persist: true, endpoint: '/api/lib/countries/'})
    this.countries.get().then()
  }
}
</script>
