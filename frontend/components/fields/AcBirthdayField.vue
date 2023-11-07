<template>
  <v-menu
      ref="menu"
      v-model="menu"
      :close-on-content-click="false"
      transition="scale-transition"
      offset-y
      min-width="290px"
      v-bind="$attrs"
  >
    <template v-slot:activator="{ props }">
      <div v-bind="props">
        <v-text-field :model-value="modelValue" v-bind="$attrs" v-on="props" prepend-icon="mdi-event"
                      readonly>
          <template v-for="name in slotNames" #[name]>
            <slot :name="name"/>
          </template>
        </v-text-field>
      </div>
    </template>
    <v-date-picker
        ref="picker"
        v-model="converted"
        v-model:view-mode="activePicker"
        :max="new Date().toISOString().slice(0, 10)"
        min="1900-01-01"
        @change="menu = false"
    />
  </v-menu>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
import {parseISO} from 'date-fns'
import {VTextField} from 'vuetify/components/VTextField'

@Component({emits: ['update:modelValue']})
class AcBirthdayField extends Vue {
  @Prop({required: true})
  public modelValue!: null | string

  public menu = false

  public activePicker: 'year' | 'month' | 'months' = 'year'

  public get converted(): null | Date {
    if (this.modelValue === null) {
      return this.modelValue
    }
    return parseISO(this.modelValue)
  }

  public get slotNames(): Array<keyof VTextField['$slots']> {
    // @ts-expect-error
    return [...Object.keys(this.$slots)]
  }

  public set converted(val: Date) {
    this.$emit('update:modelValue', this.$vuetify.date.toISO(val))
    this.menu = false
  }

  @Watch('menu')
  public setDate(toggle: boolean) {
    /* istanbul ignore else */
    if (toggle) {
      setTimeout(() => (this.activePicker = 'year'))
    }
  }

  public created() {
    // @ts-expect-error
    window.bday = this
  }
}

export default toNative(AcBirthdayField)
</script>
