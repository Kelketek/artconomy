<template>
  <ac-form-container :sending="fieldController.form.sending" :errors="fieldController.form.errors">
    <v-row no-gutters>
      <slot name="preview" :item="item" v-for="item in listController.list">
        <v-col cols="12">{{item}}</v-col>
      </slot>
      <slot name="empty" v-if="listController.empty">
      </slot>
      <v-col cols="12">
        <slot :filter="filter"/>
      </v-col>
    </v-row>
  </ac-form-container>
</template>

<script setup lang="ts">
import {ListController} from '@/store/lists/controller.ts'
import {FieldController} from '@/store/forms/field-controller.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {SingleController} from '@/store/singles/controller.ts'
import {watch} from 'vue'

const props = defineProps<{listController: ListController<any>, fieldController: FieldController}>()

const filter = (entry: {id: number}, queryText: string, itemText: string) => {
  if (!queryText) {
    return false
  }
  if (props.listController.list.map((item: SingleController<any>) => item.x.id).indexOf(entry.id) !== -1) {
    return false
  }
  return itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1
}

watch(() => props.fieldController.value, (newVal) => {
  if (newVal === null) {
    return
  }
  props.fieldController.form.submitThen(props.listController.uniquePush).then()
})
</script>
