<template>
  <div>
    <v-select
        v-model="value"
        :items="schema.values()"
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
    name: 'fieldVSelect',
    mixins: [ abstractField, materialField ],
    created () {
      window.select = this
    }
  }
</script>