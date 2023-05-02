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
import {Decimal} from 'decimal.js'

@Component
export default class AcLineItemPreview extends Vue {
  @Prop({required: true})
  public line!: LineItem

  @Prop({required: true})
  public priceData!: LineAccumulator

  @Prop({default: false})
  public editing!: boolean

  @Prop({default: false})
  public transfer!: boolean

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
    if (this.line.frozen_value !== null) {
      return new Decimal(this.line.frozen_value)
    }
    return this.priceData.subtotals.get(this.line) as Decimal
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
    if (this.line.type === LineTypes.TIP) {
      if (this.transfer) {
        return 'Tip net'
      } else {
        return 'Tip'
      }
    }
    if (this.line.type === LineTypes.DELIVERABLE_TRACKING) {
      let label = 'Order Tracking'
      if (this.line.targets?.length) {
        label += ' (' + this.line.targets.map((target) => `${target.model} #${target.id}`).join(', ') + ')'
      }
      return label
    }
    const BASIC_TYPES: {[key: number]: string} = {
      0: 'Base price',
      2: 'Shield protection',
      3: 'Landscape bonus',
      4: 'Tip net',
      5: 'Table service',
      6: 'Tax',
      7: 'Accessory item',
      8: 'Premium Subscription',
      9: 'Other Fee',
      10: 'Order Tracking',
      11: 'Processing',
    }
    return BASIC_TYPES[this.line.type] || 'Unknown'
  }
}
</script>
