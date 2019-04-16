<template>
  <v-flex>
    <v-btn icon small color="primary" class="picker-button" @click="launchPicker"><v-icon>colorize</v-icon></v-btn>
    <input v-model="scratch"
           type="color"
           class="picker"
           slot="prepend-inner"/>
  </v-flex>
</template>

<style>
  .picker {
    display: none;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'

  @Component
export default class AcColorPrepend extends Vue {
    @Prop()
    public value!: string
    public scratch = ''

    @Watch('scratch')
    public updateInput(val: string) {
      this.$emit('input', val)
    }

    public launchPicker() {
      const input = this.$el.querySelector('.picker') as HTMLInputElement
      input.click()
    }

    public created() {
      this.scratch = this.value
    }
}
</script>
