<template>
  <div>
    <v-text-field
        v-model="value"
        :label="schema.label"
        :type="schema.inputType || false"
        :rules="validators"
        :required="schema.required"
        :error-messages="errors"
        :hint="schema.hint"
        persistent-hint
    />
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import materialField from './materialField'

  export default {
    name: 'fieldVText',
    mixins: [ abstractField, materialField ],
    created () {
      window.schema = this.schema
    }
  }
</script>