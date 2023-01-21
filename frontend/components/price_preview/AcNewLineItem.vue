<template>
  <v-row no-gutters>
    <v-col class="text-left pa-1" cols="12">
      <v-btn type="submit" small>
        <v-icon left color="yellow">add</v-icon>{{ placeholder }}
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
