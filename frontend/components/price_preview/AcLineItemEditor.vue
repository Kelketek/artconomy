<template>
  <v-row no-gutters>
    <v-col class="text-right" cols="12">
      <ac-patch-field
          :patcher="line.patchers.description"
          :id="`lineItem-${line.x!.id}-description`"
          :disabled="disabled"
          density="compact"
          :placeholder="placeholder"
      />
    </v-col>
    <v-col class="text-left" cols="6">
      <ac-patch-field
          :patcher="line.patchers.amount"
          :id="`lineItem-${line.x!.id}-amount`"
          field-type="ac-price-field"
          :disabled="disabled"
          density="compact"
          @keydown.enter="newLineFunc"
      />
    </v-col>
    <v-col class="text-left" cols="4" md="5">
      <v-text-field :disabled="true" :value="'$' + price.toFixed(2)" density="compact"/>
    </v-col>
    <v-col cols="2" sm="1" class="text-center d-flex justify-center pl-1">
      <v-btn size="x-small" icon color="red" @click.prevent="line.delete" v-if="deletable" :disabled="disabled" class="align-self-start mt-1">
        <v-icon :icon="mdiDelete"/>
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import LineItem from '@/types/LineItem.ts'
import LineAccumulator from '@/types/LineAccumulator.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {Decimal} from 'decimal.js'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {LineTypes} from '@/types/LineTypes.ts'
import {mdiDelete} from '@mdi/js'
import {computed} from 'vue'

const props = withDefaults(defineProps<{
  line: SingleController<LineItem>,
  priceData: LineAccumulator,
  enableNewLine?: boolean,
  disabled?: boolean,
}>(), {
  enableNewLines: false,
  disabled: false,
})
const emit = defineEmits<{'new-line': []}>()

const deletable = computed(()  => props.line.x?.type !== LineTypes.BASE_PRICE)

const price = computed(() => props.priceData.subtotals.get(props.line.x as LineItem) as Decimal)

const newLineFunc = () => {
  if (props.enableNewLine) {
    emit('new-line')
  }
}

const placeholder = computed(() => {
  if ((props.line.x as LineItem).type === 0) {
    return 'Base price'
  }
  if ((props.line.x as LineItem).type === 1) {
    if (price.value.lt(0)) {
      return 'Discount'
    } else {
      return 'Additional requirements'
    }
  }
  const BASIC_TYPES: { [key: number]: string } = {
    0: 'Base price',
    2: 'Shield protection',
    3: 'Landscape bonus',
    4: 'Tip',
    5: 'Table service',
    6: 'Tax',
    7: 'Accessory item',
  }
  return BASIC_TYPES[(props.line.x as LineItem).type] || 'Other'
})
</script>
