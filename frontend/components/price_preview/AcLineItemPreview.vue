<template>
  <v-row no-gutters>
    <v-col class="text-right pr-1" :cols="labelCols">
      <v-tooltip :text="typeHint" v-if="typeHint">
        <template v-slot:activator="{ props }">
          <v-badge
              color="info"
              content="?"
              inline
              v-bind="props"
          />
        </template>
      </v-tooltip>
      {{label}}:
    </v-col>
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

<script setup lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import LineItem from '@/types/LineItem.ts'
import LineAccumulator from '@/types/LineAccumulator.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {Decimal} from 'decimal.js'
import {computed} from 'vue'

declare interface AcLineItemPreviewProps {
  line: LineItem,
  priceData: LineAccumulator,
  editing?: boolean,
  transfer?: boolean,
}

const props = withDefaults(defineProps<AcLineItemPreviewProps>(), {
  editing: false,
  transfer: false,
})

const labelCols = computed(() => props.editing ? 4 : 6)
const priceCols = computed(() => props.editing ? 4 : 6)

const price = computed(() => {
  if (props.line.frozen_value !== null) {
    return new Decimal(props.line.frozen_value)
  }
  return props.priceData.subtotals.get(props.line) as Decimal
})

const BASIC_TYPES: { [key: number]: string } = {
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
  12: 'Reconciliation',
}

const label = computed(() => {
  if (props.line.description) {
    return props.line.description
  }
  if (props.line.type === LineTypes.ADD_ON) {
    if (price.value.lt(0)) {
      return 'Discount'
    } else {
      return 'Additional requirements'
    }
  }
  if (props.line.type === LineTypes.TIP) {
    if (props.transfer) {
      return 'Tip net'
    } else {
      return 'Tip'
    }
  }
  if (props.line.type === LineTypes.DELIVERABLE_TRACKING) {
    let label = 'Order Tracking'
    if (props.line.targets?.length) {
      label += ' (' + props.line.targets.map((target) => `${target.model} #${target.id}`).join(', ') + ')'
    }
    return label
  }
  return BASIC_TYPES[props.line.type] || 'Unknown'
})

const TYPE_HINTS = {
  0: 'This is the portion of the initial listing price that goes to the seller. This may be less than the listing ' +
      'price if shield is enabled by default, or if a discount has been applied.',
  2: "This is a non-refundable fee for Artconomy Shield, including buyer/seller " +
      "protection and dispute resolution.",
}

const typeHint = computed(() => {
  return TYPE_HINTS[props.line.type as keyof typeof TYPE_HINTS] || ''
})

//
// @Component
// class AcLineItemPreview extends Vue {
//   @Prop({required: true})
//   public line!: LineItem
//
//   @Prop({required: true})
//   public priceData!: LineAccumulator
//
//   @Prop({default: false})
//   public editing!: boolean
//
//   @Prop({default: false})
//   public transfer!: boolean
//
//   public get labelCols() {
//     if (this.editing) {
//       return 4
//     }
//     return 6
//   }
//
//   public get priceCols() {
//     if (this.editing) {
//       return 4
//     }
//     return 4
//   }
//
//   public get price() {
//     if (this.line.frozen_value !== null) {
//       return new Decimal(this.line.frozen_value)
//     }
//     return this.priceData.subtotals.get(this.line) as Decimal
//   }
//
//   public get label() {
//     if (this.line.description) {
//       return this.line.description
//     }
//     if (this.line.type === LineTypes.ADD_ON) {
//       if (this.price.lt(0)) {
//         return 'Discount'
//       } else {
//         return 'Additional requirements'
//       }
//     }
//     if (this.line.type === LineTypes.TIP) {
//       if (this.transfer) {
//         return 'Tip net'
//       } else {
//         return 'Tip'
//       }
//     }
//     if (this.line.type === LineTypes.DELIVERABLE_TRACKING) {
//       let label = 'Order Tracking'
//       if (this.line.targets?.length) {
//         label += ' (' + this.line.targets.map((target) => `${target.model} #${target.id}`).join(', ') + ')'
//       }
//       return label
//     }
//     const BASIC_TYPES: { [key: number]: string } = {
//       0: 'Base price',
//       2: 'Shield protection',
//       3: 'Landscape bonus',
//       4: 'Tip net',
//       5: 'Table service',
//       6: 'Tax',
//       7: 'Accessory item',
//       8: 'Premium Subscription',
//       9: 'Other Fee',
//       10: 'Order Tracking',
//       11: 'Processing',
//       12: 'Reconciliation',
//     }
//     return BASIC_TYPES[this.line.type] || 'Unknown'
//   }
// }
//
// export default toNative(AcLineItemPreview)
</script>
