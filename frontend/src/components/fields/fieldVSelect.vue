<template>
  <div>
    <v-select
        v-model="selection"
        :id="'field-' + schema.model"
        :items="items"
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
    computed: {
      selection: {
        get () {
          if (this.value === undefined || this.value === null) {
            return this.value
          }
          return this.value + ''
        },
        set (value) {
          this.value = value
        }
      },
      items () {
        if (Array.isArray(this.schema.values)) {
          return this.schema.values
        }
        return this.schema.values()
      }
    },
    created () {
      window.select = this
    }
  }
</script>