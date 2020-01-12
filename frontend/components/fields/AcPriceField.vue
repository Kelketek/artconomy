<template>
  <v-text-field :value="value" @input="update" v-bind="$attrs" prefix="$" @blur="blur" class="price-input">
    <slot v-for="(_, name) in $slots" :name="name" :slot="name"/>
  </v-text-field>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop, Watch} from 'vue-property-decorator'
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
        this.update(parseFloat(rawValue).toFixed(2))
      })
    }

    public mounted() {
      if (this.value) {
        this.update(parseFloat(this.value).toFixed(2))
      }
    }
}
</script>
