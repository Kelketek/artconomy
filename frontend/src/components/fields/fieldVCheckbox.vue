<template>
  <div>
    <v-checkbox
        v-model="value"
        :label="schema.label"
        :rules="validators"
        :required="schema.required"
        :hint="schema.hint"
        :error-messages="errors"
        persistent-hint
    />
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import materialField from './materialField'

  export default {
    name: 'fieldVCheckbox',
    mixins: [ abstractField, materialField ]
  }
</script>