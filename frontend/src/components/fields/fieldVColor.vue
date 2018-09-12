<template>
  <v-layout row>
    <v-flex xs11>
      <v-text-field
          v-model="color"
          :label="schema.label"
          :rules="validators"
          :required="schema.required"
          :hint="schema.hint"
          :error-messages="errors"
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
    },
    computed: {
      color: {
        get () {
          return this.value
        },
        set (newVal) {
          newVal = newVal.replace(new RegExp('[\\W]*', 'g'), '')
          newVal = newVal.toLowerCase()
          newVal = '#' + newVal
          this.value = newVal
        }
      }
    }
  }
</script>