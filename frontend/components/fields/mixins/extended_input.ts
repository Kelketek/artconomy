import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import Component from 'vue-class-component'

@Component
export default class ExtendedInput extends Vue {
  @Prop()
  public label!: string

  @Prop({default: () => []})
  public errorMessages!: string[]

  private get passedProps() {
    const props = {...this.$props}
    delete props.label
    delete props.success
    return props
  }

  private get errorColor() {
    if (this.errorFocused) {
      return 'red'
    }
    return 'primary'
  }

  private get errorFocused() {
    return !!this.errorMessages.length
  }
}
