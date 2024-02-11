<template>
  <v-col cols="12" class="text-center">
    <v-btn
        @click="page = page > 1 ? page - 1 : page"
        :disabled="page === 1"
        class="mr-1"
        color="primary"
    >Prev</v-btn>
    <span>{{ page }} / {{ pages }}</span>
    <v-btn
        @click="page = page < pages ? page + 1 : page"
        color="primary"
        :disabled="page === pages" class="ml-1"
    >Next</v-btn>
  </v-col>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'

const props = defineProps<{modelValue: number, pages: number}>()
const emit = defineEmits<{'update:modelValue': [value: number]}>()
const page = ref(props.modelValue)
watch(page, () => emit('update:modelValue', page.value))
watch(() => props.modelValue, (newVal) => page.value = newVal)
</script>
