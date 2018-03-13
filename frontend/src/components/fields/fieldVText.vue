<template>
  <div>
    <v-text-field
        v-model="value"
        :id="'field-' + schema.model"
        :label="schema.label"
        :type="schema.inputType"
        :rules="validators"
        :required="schema.required"
        :error-messages="errors"
        :hint="schema.hint"
        :multi-line="schema.multiLine"
        :placeholder="schema.placeholder"
        :mask="schema.mask"
        :step="schema.step"
        :min="schema.min"
        :max="schema.max"
        :persistent-hint="true"
        :counter="schema.counter"
    />
  </div>
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import materialField from './materialField'

  export default {
    name: 'fieldVText',
    mixins: [ abstractField, materialField ]
  }
</script>