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
    <template v-slot:activator="{ on }">
      <v-text-field :value="value" v-bind="$attrs" v-on="on" prepend-icon="event"
                    readonly>
        <slot v-for="(_, name) in $slots" :name="name" :slot="name"/>
      </v-text-field>
    </template>
    <v-date-picker
      ref="picker"
      v-model="scratch"
      :max="new Date().toISOString().substr(0, 10)"
      min="1900-01-01"
      @change="update"
    ></v-date-picker>
  </v-menu>
</template>

<script lang="ts">
import Vue from 'vue'
import {Prop, Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'

@Component
export default class AcBirthdayField extends Vue {
  @Prop({required: true})
  public value!: string

  public scratch: null|string = null

  public menu = false

  @Watch('menu')
  public setDate(toggle: boolean) {
    /* istanbul ignore else */
    if (toggle) {
      setTimeout(() => ((this.$refs.picker as any).activePicker = 'YEAR'))
    }
  }

  @Watch('value')
  public updateScratch(val: null|string) {
    this.scratch = val
  }

  @Watch('scratch')
  public update(value: string) {
    this.$emit('input', value)
  }

  public created() {
    this.scratch = this.value
  }
}
</script>
