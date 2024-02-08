<template>
  <ac-bound-field :field="form.fields.name"></ac-bound-field>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component({
    components: {AcBoundField},
  })
class BoundField extends ArtVue {
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
export default toNative(BoundField)
</script>
