<template>
  <v-rating :model-value="modelValue" @update:model-value="update"></v-rating>
</template>

<style>
.v-rating .v-icon {
  padding: 0;
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'

@Component({emits: ['update:modelValue']})
class AcStarField extends Vue {
  @Prop({required: true})
  public modelValue!: number

  public update(val: number|string) {
    let result: number
    if (typeof val === 'number') {
      result = val
    } else {
      result = parseInt(val, 10)
    }
    this.$emit('update:modelValue', result)
  }
}

export default toNative(AcStarField)
</script>
