<template>
  <v-row no-gutters>
    <v-col class="text-right pr-1" cols="4"><ac-bound-field :field="form.fields.description" :placeholder="placeholder" /></v-col>
    <v-col class="text-left pl-1" cols="4"><ac-bound-field :field="form.fields.amount" field-type="ac-price-field" /></v-col>
    <v-col class="text-left pl-1" cols="2"><v-text-field :value="'$' + price.toFixed(2)" :disabled="true"></v-text-field></v-col>
    <v-col cols="2" align-self="center" class="text-center">
      <v-btn x-small fab color="black" type="submit" :class="{glowing: worthSaving}">
        <v-icon color="yellow">save</v-icon>
      </v-btn>
    </v-col>
  </v-row>
</template>

<style>
  @keyframes shadow-pulse
  {
    0% {
      box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.5);
    }
    100% {
      box-shadow: 0 0 0 35px rgba(0, 0, 0, 0);
    }
  }

  .glowing {
    animation: shadow-pulse 1s infinite;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import Component from 'vue-class-component'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {LineTypes} from '@/types/LineTypes'
@Component({
  components: {AcBoundField},
})
export default class AcNewLineItem extends Vue {
  @Prop({required: true})
  public form!: FormController

  @Prop({required: true})
  public price!: number

  public get worthSaving() {
    return ![NaN, Infinity, 0].includes(parseFloat(this.form.fields.amount.value))
  }

  public get placeholder() {
    if (this.form.fields.type.value === LineTypes.ADD_ON) {
      return 'Surcharge/Discount'
    }
    if (this.form.fields.type.value === LineTypes.EXTRA) {
      return 'Extra item'
    }
    return 'Other'
  }
}
</script>
