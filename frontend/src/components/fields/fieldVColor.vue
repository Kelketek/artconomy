<template>
  <v-layout row>
    <v-flex xs11>
      <v-text-field
          v-model="value"
          :label="schema.label"
          :rules="validators"
          :required="schema.required"
          :hint="schema.hint"
          persistent-hint
      />
    </v-flex>
    <v-flex xs1>
      <input type="color" v-model="value" />
    </v-flex>
  </v-layout>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import materialField from './materialField'

  export default {
    name: 'fieldVColor',
    mixins: [ abstractField, materialField ],
    created () {
      window.select = this
    }
  }
</script>