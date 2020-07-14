<template>
  <ac-bound-field :field="form.fields.name"></ac-bound-field>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcBoundField from '@/components/fields/AcBoundField'
import {FormController} from '@/store/forms/form-controller'

  @Component({
    components: {AcBoundField},
  })
export default class BoundField extends Vue {
    public form: FormController = null as unknown as FormController

    public created() {
      this.form = this.$getForm('boundFields', {
        endpoint: '/',
        fields: {
          name: {value: 'Wat'},
          age: {value: 20},
        },
      })
    }
}
</script>
