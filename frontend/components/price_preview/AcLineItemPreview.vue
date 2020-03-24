<template>
  <v-row no-gutters>
    <v-col class="text-right pr-1" :cols="labelCols">{{label}}:</v-col>
    <v-col v-if="editing" cols="4">
      <span v-if="line.back_into_percentage && line.percentage">(*)</span>
      <span v-if="line.cascade_percentage && line.percentage">(</span>
      <span v-if="line.percentage">{{line.percentage.toFixed(2)}}%</span>
      <span v-if="line.cascade_percentage && line.percentage">)</span>
      <span v-if="line.percentage && line.amount">&nbsp;+&nbsp;</span>
      <span v-if="line.cascade_amount && line.amount">(</span>
      <span v-if="line.amount">${{line.amount.toFixed(2)}}</span>
      <span v-if="line.cascade_amount && line.amount">)</span>
    </v-col>
    <v-col class="text-left pl-1" :cols="priceCols">${{price.toFixed(2)}}</v-col>
  </v-row>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import LineItem from '@/types/LineItem'
import Component from 'vue-class-component'
import LineAccumulator from '@/types/LineAccumulator'
import {LineTypes} from '@/types/LineTypes'
import Big from 'big.js'

@Component
export default class AcLineItemPreview extends Vue {
  @Prop({required: true})
  public line!: LineItem
  @Prop({required: true})
  public priceData!: LineAccumulator
  @Prop({default: false})
  public editing!: boolean

  public get labelCols() {
    if (this.editing) {
      return 4
    }
    return 6
  }

  public get priceCols() {
    if (this.editing) {
      return 4
    }
    return 4
  }

  public get price() {
    return this.priceData.map.get(this.line) as Big
  }

  public get label() {
    if (this.line.description) {
      return this.line.description
    }
    if (this.line.type === LineTypes.ADD_ON) {
      if (this.price.lt(0)) {
        return 'Discount'
      } else {
        return 'Additional requirements'
      }
    }
    const BASIC_TYPES: {[key: number]: string} = {
      0: 'Base price',
      2: 'Shield protection',
      3: 'Landscape bonus',
      4: 'Tip',
      5: 'Table service',
      6: 'Tax',
      7: 'Accessory item',
    }
    return BASIC_TYPES[this.line.type]
  }
}
</script>
