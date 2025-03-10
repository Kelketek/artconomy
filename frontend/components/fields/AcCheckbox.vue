<template>
  <v-checkbox v-model="scratch">
    <!-- @ts-nocheck -->
    <template
      v-for="name in slotNames"
      #[name]
    >
      <slot :name="name" />
    </template>
  </v-checkbox>
</template>

<script setup lang="ts">
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {computed, ref, useSlots, watch} from 'vue'

const emit = defineEmits<{'update:modelValue': [boolean]}>()
const props = defineProps<{modelValue: boolean}>()

const scratch = ref(props.modelValue)

watch(() => props.modelValue, (val: boolean) => {
  scratch.value = val
})

watch(scratch, (val: boolean | null) => {
  emit('update:modelValue', !!val)
})

const slots = useSlots()

const slotNames = computed((): Array<keyof VCheckbox['$slots']> => {
  // @ts-expect-error
  return [...Object.keys(slots)]
})
</script>
