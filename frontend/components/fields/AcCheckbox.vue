<template>
  <v-checkbox v-model="scratch" v-bind="$attrs">
    <slot v-for="(_, name) in $slots" :name="name" :slot="name"/>
  </v-checkbox>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop, Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'

@Component
export default class AcCheckbox extends Vue {
  @Prop({required: true})
  public value!: boolean

  public scratch = false

  @Watch('scratch', {immediate: true})
  public fixFalse(val: boolean|null) {
    this.$emit('input', !!val)
  }

  created() {
    this.scratch = this.value
  }
}
</script>
