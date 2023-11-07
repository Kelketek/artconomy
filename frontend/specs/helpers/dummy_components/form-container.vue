<template>
  <v-col>
    <ac-form-container ref="defaultForm" />
    <ac-form-container ref="errorForm" :errors="basicForm.errors" :sending="basicForm.sending" />
  </v-col>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import {ArtVue} from '@/lib/lib'

@Component({
  components: {AcFormContainer},
})
class FormContainer extends ArtVue {
  public basicForm: FormController = null as unknown as FormController
  public created() {
    this.basicForm = this.$getForm('basicForm', {endpoint: '/endpoint/', fields: {}})
  }
}
export default toNative(FormContainer)
</script>
