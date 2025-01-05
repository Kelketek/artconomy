<template>
  <v-btn @click="dialog = true"><v-icon left>{{mdiGavel}}</v-icon>Kill submission</v-btn>
  <ac-form-dialog
    v-model="dialog"
    v-bind="killForm.bind"
    @submit="killForm.submitThen(goBack)"
    title="Kill Submission"
  >
    <v-row>
      <v-row cols="12" class="pa-3">
        <v-alert type="warning">This will kill this submission. Depending on the type of infraction, it may be impossible to ever upload this piece again.</v-alert>
      </v-row>
      <v-col cols="12">
        <ac-bound-field label="Reason" :field="killForm.fields.flag" field-type="v-select" :item-props="true" :items="killReasons" />
      </v-col>
      <v-col cols="12">
        <ac-bound-field label="Comment" :field="killForm.fields.comment" field-type="v-text-field" />
      </v-col>
    </v-row>
  </ac-form-dialog>
</template>

<style scoped>

</style>

<script setup lang="ts">
import {mdiGavel} from '@mdi/js'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {computed, ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import type {SingleController} from '@/store/singles/controller.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {FLAGS_SHORT} from '@/lib/lib.ts'
import {ReportFlags} from '@/types/enums/ReportFlags.ts'
import {useRouter} from 'vue-router'


const props = defineProps<{controller: SingleController<any>}>()
// Any compatible resource should have a /kill/ URL that handles this need.
const url = computed(() => `${props.controller.endpoint}kill/`)
const dialog = ref(false)
const router = useRouter()

const killForm = useForm(`killForm${props.controller.name.value}`, {endpoint: url.value, fields: {flag: {value: null, validators: [{name: 'required'}]}, comment: {value: ''}}})
const killReasons = computed(() => {
  const options = Object.entries(FLAGS_SHORT).filter(([value, _]) => parseInt(value, 10) > ReportFlags.IMPROPERLY_RATED)
  return options.map(([value, title]) => ({title, value}))
})
const goBack = () => {
  if (window.history.length) {
    router.back()
  } else {
    router.replace({name: 'Home'})
  }
}
</script>
