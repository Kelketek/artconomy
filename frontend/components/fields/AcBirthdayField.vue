<template>
  <v-menu
      ref="menu"
      v-model="menuToggle"
      :close-on-content-click="false"
      transition="scale-transition"
      offset-y
      min-width="290px"
      v-bind="attrs"
  >
    <template v-slot:activator="{ props }">
      <div v-bind="props">
        <v-text-field :model-value="modelValue" v-bind="attrs" v-on="props" prepend-icon="mdi-event"
                      readonly>
          <template v-for="name in slotNames" #[name]>
            <slot :name="name"/>
          </template>
        </v-text-field>
      </div>
    </template>
    <v-date-picker
        ref="picker"
        v-model="converted"
        v-model:view-mode="activePicker"
        :max="new Date().toISOString().slice(0, 10)"
        min="1900-01-01"
        @change="menuToggle = false"
    />
  </v-menu>
</template>

<script setup lang="ts">
import {format, parseISO} from 'date-fns'
import {VTextField} from 'vuetify/components/VTextField'
import {computed, ref, useAttrs, useSlots, watch} from 'vue'
import {VDatePicker, VMenu} from 'vuetify/components'

const props = defineProps<{modelValue: null|string}>()
const menuToggle = ref(false)
const menu = ref<typeof VMenu|null>(null)
const picker = ref<typeof VDatePicker|null>(null)
const activePicker = ref<'year' | 'month' | 'months'>('year')
const emit = defineEmits<{'update:modelValue': [string|null]}>()
const slots = useSlots()
const attrs = useAttrs()

const converted = computed({
  get(): null|Date {
    if (props.modelValue === null) {
      return props.modelValue
    }
    return parseISO(props.modelValue)
  },
  set(val: Date|null) {
    if (val === null) {
      emit('update:modelValue', null)
    } else {
      emit('update:modelValue', format(val, 'yyyy-MM-dd'))
    }
    menuToggle.value = false
  }
})

const slotNames = computed(() => {
  return Object.keys(slots) as Array<keyof VTextField['$slots']>
})

watch(menuToggle, (toggle: boolean) => {
  if (toggle) {
    setTimeout(() => activePicker.value = 'year')
  }
})

// Used in tests.
defineExpose({menu, picker, activePicker})
</script>
