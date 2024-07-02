<template>
  <v-row no-gutters>
    <v-col class="text-left pa-1" cols="12">
      <v-btn type="submit" small variant="flat" color="black">
        <v-icon left color="yellow" :icon="mdiPlus"/>
        {{ placeholder }}
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {FormController} from '@/store/forms/form-controller.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {computed} from 'vue'
import {mdiPlus} from '@mdi/js'

const props = defineProps<{form: FormController}>()
const placeholder = computed(() => {
  if (props.form.fields.type.value === LineTypes.ADD_ON) {
    return 'Surcharge/Discount'
  }
  if (props.form.fields.type.value === LineTypes.EXTRA) {
    return 'Extra item'
  }
  return 'Other'
})
</script>
