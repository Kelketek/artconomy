<template>
  <v-text-field :model-value="modelValue" @update:model-value="update" v-bind="$attrs" prefix="$" ref="input" @blur="blur"
                class="price-input">
    <template v-for="name in slotNames" #[name]>
      <slot :name="name"/>
    </template>
  </v-text-field>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'

@Component({emits: ['update:modelValue']})
class AcPriceField extends Vue {
  @Prop({required: true})
  public modelValue!: string

  public update(value: string) {
    this.$emit('update:modelValue', value)
  }

  public get slotNames(): Array<keyof VTextField['$slots']> {
    // @ts-expect-error
    return [...Object.keys(this.$slots)]
  }

  public blur() {
    this.$nextTick(() => {
      const rawValue = this.modelValue
      const newVal = parseFloat(rawValue)
      /* istanbul ignore if */
      if (isNaN(newVal)) {
        return
      }
      this.update(newVal.toFixed(2))
    })
  }
}

export default toNative(AcPriceField)
</script>
