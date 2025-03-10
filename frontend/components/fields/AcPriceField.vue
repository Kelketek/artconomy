<template>
  <v-text-field
    v-bind="attrs"
    ref="input"
    :model-value="modelValue"
    prefix="$"
    class="price-input"
    @update:model-value="update"
    @blur="blur"
  >
    <template
      v-for="name in slotNames"
      #[name]
    >
      <slot :name="name" />
    </template>
  </v-text-field>
</template>

<script setup lang="ts">
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {computed, nextTick, useAttrs, useSlots} from 'vue'

const emit = defineEmits<{'update:modelValue': [string]}>()
const props = defineProps<{modelValue: string|number}>()
const slots = useSlots()
const attrs = useAttrs()

const update = (value: string) => {
  emit('update:modelValue', value)
}

const blur = () => {
  nextTick(() => {
    const rawValue = props.modelValue
    const newVal = parseFloat(`${rawValue}`)
    /* istanbul ignore if */
    if (isNaN(newVal)) {
      return
    }
    update(newVal.toFixed(2))
  })
}

const slotNames = computed((): Array<keyof VTextField['$slots']> => {
  // @ts-expect-error
  return [...Object.keys(slots)]
})
</script>
