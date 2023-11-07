<template>
  <div class="flex">
    <v-btn icon small color="primary" class="picker-button" @click="launchPicker">
      <v-icon icon="mdi-colorize"/>
    </v-btn>
    <input v-model="scratch"
           type="color"
           class="picker"
    />
  </div>
</template>

<style>
.picker {
  display: none;
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'

@Component({emits: ['update:modelValue']})
class AcColorPrepend extends Vue {
  @Prop()
  public modelValue!: string

  public scratch = ''

  @Watch('scratch')
  public updateInput(val: string) {
    this.$emit('update:modelValue', val)
  }

  public launchPicker() {
    const input = this.$el.querySelector('.picker') as HTMLInputElement
    input.click()
  }

  public created() {
    this.scratch = this.modelValue
  }
}

export default toNative(AcColorPrepend)
</script>
