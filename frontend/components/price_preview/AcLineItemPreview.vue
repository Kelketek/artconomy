<template>
  <v-row no-gutters>
    <v-col class="text-right pr-1" :cols="labelCols">
      <v-tooltip v-if="typeHint" :text="typeHint">
        <template #activator="activator">
          <v-badge color="info" content="?" inline v-bind="activator.props" />
        </template>
      </v-tooltip>
      {{ label }}:
    </v-col>
    <v-col v-if="editing" cols="4">
      <span v-if="line.back_into_percentage && line.percentage">(*)</span>
      <span v-if="line.percentage">{{ line.percentage }}%</span>
      <span v-if="line.percentage && line.amount">&nbsp;+&nbsp;</span>
      <span v-if="line.amount">${{ line.amount }}</span>
    </v-col>
    <v-col class="text-left pl-1" :cols="priceCols"> ${{ price }} </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { LineType } from "@/types/enums/LineType.ts"
import { computed } from "vue"
import type { LineAccumulator, LineItem } from "@/types/main"

declare interface AcLineItemPreviewProps {
  line: LineItem
  priceData: LineAccumulator
  editing?: boolean
  transfer?: boolean
}

const props = withDefaults(defineProps<AcLineItemPreviewProps>(), {
  editing: false,
  transfer: false,
})

const labelCols = computed(() => (props.editing ? 4 : 6))
const priceCols = computed(() => (props.editing ? 4 : 6))

const price = computed(() => {
  if (props.line.frozen_value !== null) {
    return props.line.frozen_value
  }
  return props.priceData.subtotals.get(props.line) as string
})

const BASIC_TYPES: { [key: number]: string } = {
  [LineType.BASE_PRICE]: "Base price",
  [LineType.SHIELD]: "Shield protection",
  [LineType.BONUS]: "Landscape bonus",
  [LineType.TIP]: "Tip net",
  [LineType.TABLE_SERVICE]: "Table service",
  [LineType.TAX]: "Tax",
  [LineType.EXTRA]: "Accessory item",
  [LineType.PREMIUM_SUBSCRIPTION]: "Premium Subscription",
  [LineType.OTHER_FEE]: "Other Fee",
  [LineType.DELIVERABLE_TRACKING]: "Order Tracking",
  [LineType.PROCESSING]: "Handling fee",
  [LineType.RECONCILIATION]: "Reconciliation",
  [LineType.CARD_FEE]: "Card Processing",
  [LineType.CROSS_BORDER_TRANSFER_FEE]: "Cross-border transfer fee",
  [LineType.PAYOUT_FEE]: "Payout fee",
  [LineType.CONNECT_FEE]: "Connect fee",
}

const label = computed(() => {
  if (props.line.description) {
    return props.line.description
  }
  if (props.line.type === LineType.ADD_ON) {
    if (parseFloat(price.value) < 0) {
      return "Discount"
    } else {
      return "Additional requirements"
    }
  }
  if (props.line.type === LineType.TIP) {
    if (props.transfer) {
      return "Tip net"
    } else {
      return "Tip"
    }
  }
  if (props.line.type === LineType.DELIVERABLE_TRACKING) {
    let label = "Order Tracking"
    if (props.line.targets?.length) {
      label +=
        " (" +
        props.line.targets
          .map((target) => `${target.model} #${target.id}`)
          .join(", ") +
        ")"
    }
    return label
  }
  return BASIC_TYPES[props.line.type] || "Unknown"
})

const TYPE_HINTS = {
  [LineType.BASE_PRICE]:
    "This is the portion of the initial listing price that goes to the seller. This may be less than the listing " +
    "price if shield is enabled by default, or if a discount has been applied.",
  [LineType.ADD_ON]:
    "This is a manually added line item from the seller. If the description is not clear, please ask them for details.",
  [LineType.SHIELD]:
    "Fee for Artconomy Shield, including buyer/seller " +
    "protection and dispute resolution.",
  [LineType.TIP]:
    "How much money the artist is expected to receive from the tip after all processing fees have been deducted",
  [LineType.TABLE_SERVICE]:
    "Cost to offset running convention table where you placed this order",
  [LineType.PROCESSING]:
    "Artconomy's fee to maintain the transaction system and offset risk.",
  [LineType.CARD_FEE]:
    "Blended rate from our card processor for processing a credit card transaction.",
  [LineType.CROSS_BORDER_TRANSFER_FEE]:
    "Fee our payment processor charges for sending money internationally",
  [LineType.PAYOUT_FEE]:
    "Fee our payment processor charges to pay out to an artist's bank account",
  [LineType.CONNECT_FEE]:
    "Fee our payment processor charges for having an active artist account in a given month",
  [LineType.DELIVERABLE_TRACKING]:
    "Fee for tracking this order, invoiced to the artist at the end of the month, but included here to ensure it's accounted for in the price",
}

const typeHint = computed(() => {
  return TYPE_HINTS[props.line.type as keyof typeof TYPE_HINTS] || ""
})
</script>
