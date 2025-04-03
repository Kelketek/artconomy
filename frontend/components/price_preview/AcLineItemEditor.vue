<template>
  <v-row no-gutters>
    <v-col class="text-right" cols="12">
      <ac-patch-field
        :id="`lineItem-${line.x!.id}-description`"
        :patcher="line.patchers.description"
        :disabled="disabled"
        density="compact"
        :placeholder="placeholder"
      />
    </v-col>
    <v-col class="text-left" cols="6">
      <ac-patch-field
        :id="`lineItem-${line.x!.id}-amount`"
        :patcher="line.patchers.amount"
        field-type="ac-price-field"
        :disabled="disabled"
        density="compact"
        @keydown.enter="newLineFunc"
      />
    </v-col>
    <v-col class="text-left" cols="4" md="5">
      <v-text-field :disabled="true" :value="'$' + price" density="compact" />
    </v-col>
    <v-col cols="2" sm="1" class="text-center d-flex justify-center pl-1">
      <v-btn
        v-if="deletable"
        size="x-small"
        icon
        color="red"
        :disabled="disabled"
        class="align-self-start mt-1"
        aria-label="Delete"
        @click.prevent="line.delete"
      >
        <v-icon :icon="mdiDelete" />
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { SingleController } from "@/store/singles/controller.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { LineType } from "@/types/enums/LineType.ts"
import { mdiDelete } from "@mdi/js"
import { computed } from "vue"
import type { LineAccumulator, LineItem } from "@/types/main"

const props = withDefaults(
  defineProps<{
    line: SingleController<LineItem>
    priceData: LineAccumulator
    enableNewLine?: boolean
    disabled?: boolean
  }>(),
  {
    enableNewLines: false,
    disabled: false,
  },
)
const emit = defineEmits<{ "new-line": [] }>()

const deletable = computed(() => props.line.x?.type !== LineType.BASE_PRICE)

const price = computed(
  () => props.priceData.subtotals.get(props.line.x as LineItem)!,
)

const newLineFunc = () => {
  if (props.enableNewLine) {
    emit("new-line")
  }
}

const placeholder = computed(() => {
  if ((props.line.x as LineItem).type === 0) {
    return "Base price"
  }
  if ((props.line.x as LineItem).type === 1) {
    if (parseFloat(price.value) < 0) {
      return "Discount"
    } else {
      return "Additional requirements"
    }
  }
  const BASIC_TYPES: { [key: number]: string } = {
    0: "Base price",
    2: "Shield protection",
    3: "Landscape bonus",
    4: "Tip",
    5: "Table service",
    6: "Tax",
    7: "Accessory item",
  }
  return BASIC_TYPES[(props.line.x as LineItem).type] || "Other"
})
</script>
