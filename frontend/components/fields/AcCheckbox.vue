<template>
  <v-checkbox v-model="scratch" v-bind="$attrs">
    <!-- @ts-nocheck -->
    <template #[name] v-for="name in slotNames">
      <slot :name="name"/>
    </template>
  </v-checkbox>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'

@Component({emits: ['update:modelValue']})
class AcCheckbox extends Vue {
  @Prop({required: true})
  public modelValue!: boolean

  public scratch = false

  public get slotNames(): Array<keyof VCheckbox['$slots']> {
    // @ts-expect-error
    return [...Object.keys(this.$slots)]
  }

  @Watch('modelValue')
  public updateScratch(val: boolean) {
    this.scratch = val
  }

  @Watch('scratch')
  public fixFalse(val: boolean | null) {
    this.$emit('update:modelValue', !!val)
  }

  created() {
    this.scratch = this.modelValue
  }
}

export default toNative(AcCheckbox)
</script>
