<template>
  <v-text-field :model-value="modelValue" @update:model-value="update" v-bind="attrs" prefix="$" ref="input" @blur="blur"
                class="price-input">
    <template v-for="name in slotNames" #[name]>
      <slot :name="name"/>
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
