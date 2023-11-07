<template>
  <v-row no-gutters>
    <v-col class="text-left pa-1" cols="12">
      <v-btn type="submit" small variant="flat" color="black">
        <v-icon left color="yellow" icon="mdi-plus"/>
        {{ placeholder }}
      </v-btn>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {LineTypes} from '@/types/LineTypes'

@Component({
  components: {AcBoundField},
})
class AcNewLineItem extends Vue {
  @Prop({required: true})
  public form!: FormController

  @Prop({required: true})
  public price!: number

  public get placeholder() {
    if (this.form.fields.type.value === LineTypes.ADD_ON) {
      return 'Surcharge/Discount'
    }
    if (this.form.fields.type.value === LineTypes.EXTRA) {
      return 'Extra item'
    }
    return 'Other'
  }
}

export default toNative(AcNewLineItem)
</script>
