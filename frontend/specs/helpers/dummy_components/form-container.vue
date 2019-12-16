<template>
  <v-col>
    <ac-form-container ref="defaultForm"></ac-form-container>
    <ac-form-container ref="errorForm" :errors="basicForm.errors" :sending="basicForm.sending"></ac-form-container>
  </v-col>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'

  @Component({
    components: {AcFormContainer},
  })
export default class FormContainer extends Vue {
    public basicForm: FormController = null as unknown as FormController
    public created() {
      this.basicForm = this.$getForm('basicForm', {endpoint: '/endpoint/', fields: {}})
    }
}
</script>
