<template>
  <div>
    <v-checkbox
        v-model="value"
        :label="schema.label"
        :rules="validators"
        :required="schema.required"
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