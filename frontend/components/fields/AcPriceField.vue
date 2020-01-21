<template>
  <v-text-field :value="value" @input="update" v-bind="$attrs" prefix="$" @blur="blur" class="price-input">
    <slot v-for="(_, name) in $slots" :name="name" :slot="name"/>
  </v-text-field>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import Component from 'vue-class-component'

@Component
export default class AcPriceField extends Vue {
  @Prop({required: true})
  public value!: string

  public update(value: string) {
    this.$emit('input', value)
  }

  public blur() {
    this.$nextTick(() => {
      const rawValue = this.value
      const newVal = parseFloat(rawValue)
      /* istanbul ignore if */
      if (isNaN(newVal)) {
        return
      }
      this.update(newVal.toFixed(2))
    })
  }
}
</script>
