<template>
  <div class="flex">
    <v-btn icon variant="plain" size="x-small" color="primary" class="picker-button" @click="launchPicker">
      <v-icon size="x-large" icon="mdi-eyedropper"/>
    </v-btn>
    <input v-model="model"
           type="color"
           class="picker"
           ref="picker"
    />
  </div>
</template>

<style>
.picker {
  display: none;
}
</style>

<script setup lang="ts">

import {ref} from 'vue'

const model = defineModel<string>()
const picker = ref<HTMLInputElement|null>(null)

const launchPicker = () => {
  if (!picker.value) {
    return
  }
  picker.value.click()
}

// import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
//
// @Component({emits: ['update:modelValue']})
// class AcColorPrepend extends Vue {
//   @Prop()
//   public modelValue!: string
//
//   public scratch = ''
//
//   @Watch('scratch')
//   public updateInput(val: string) {
//     this.$emit('update:modelValue', val)
//   }
//
//   public launchPicker() {
//     const input = this.$el.querySelector('.picker') as HTMLInputElement
//     input.click()
//   }
//
//   public created() {
//     this.scratch = this.modelValue
//   }
// }
//
// export default toNative(AcColorPrepend)
</script>
