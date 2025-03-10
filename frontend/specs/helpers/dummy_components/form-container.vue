<template>
  <v-col>
    <ac-form-container ref="defaultForm" />
    <ac-form-container
      ref="errorForm"
      :errors="basicForm.errors"
      :sending="basicForm.sending"
    />
  </v-col>
</template>

<script setup lang="ts">
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {useForm} from '@/store/forms/hooks.ts'

const basicForm = useForm('basicForm', {endpoint: '/endpoint/', fields: {}})
</script>
