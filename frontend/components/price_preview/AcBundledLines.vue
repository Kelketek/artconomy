<template>
  <v-container fluid class="pa-0">
    <v-row no-gutters>
      <v-col cols="6" class="text-right align-content-center">
        <v-tooltip v-if="hint" :text="hint">
          <template #activator="activator">
            <v-badge color="info" content="?" inline v-bind="activator.props" />
          </template>
        </v-tooltip>
        {{ label }}:
      </v-col>
      <v-col cols="4" class="pl-1 text-left align-content-center"
        ><span :class="{ concealed: open }" :aria-hidden="!open"
          >${{ subtotal }}</span
        ><v-btn
          v-if="nonZero"
          size="xs"
          icon
          color="info"
          class="align-self-start my-0 ml-2 py-0"
          :aria-label="open ? 'Collapse' : 'Expand'"
          @click="toggle"
        >
          <v-icon v-if="open" :icon="mdiMinus" />
          <v-icon v-else :icon="mdiPlus" />
        </v-btn>
      </v-col>
    </v-row>
    <template v-if="open">
      <v-divider></v-divider>
      <ac-line-item-preview
        v-for="line in lines"
        :key="line.id"
        :line="line"
        :price-data="priceData"
        :editing="editing"
        :transfer="transfer"
      />
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, Ref, computed } from "vue"
import { LineAccumulator, LineItem } from "@/types/main"
import AcLineItemPreview from "@/components/price_preview/AcLineItemPreview.vue"
import { mdiMinus, mdiPlus } from "@mdi/js"
import { sum } from "@/lib/lineItemFunctions.ts"

const props = withDefaults(
  defineProps<{
    lines: LineItem[]
    editing?: boolean
    label: string
    priceData: LineAccumulator
    transfer?: boolean
    hint?: string
    modelValue?: boolean
  }>(),
  { transfer: false, editable: false, modelValue: undefined, hint: "" },
)
const emits = defineEmits<{ "update:modelValue": [boolean] }>()

const innerModel: Ref<boolean> = ref(!!props.modelValue)

const rawOpen = computed(() => {
  if (props.modelValue !== undefined) {
    return props.modelValue
  }
  return innerModel.value
})

const open = computed(() => {
  if (rawOpen.value && parseFloat(subtotal.value) !== 0) {
    return rawOpen.value
  }
  return false
})

const subtotal = computed(() => {
  return sum(
    props.lines.map(
      (line) => line.frozen_value || props.priceData.subtotals.get(line)!,
    ),
  )
})

const nonZero = computed(() => parseFloat(subtotal.value) !== 0)

const toggle = () => {
  if (props.modelValue !== undefined) {
    emits("update:modelValue", !open.value)
    return
  }
  innerModel.value = !open.value
}
</script>

<style scoped>
.concealed {
  opacity: 0;
}
</style>
