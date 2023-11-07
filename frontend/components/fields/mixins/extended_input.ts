import {Component, Prop} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib'

@Component
export default class ExtendedInput extends ArtVue {
  @Prop()
  public label!: string

  @Prop({default: () => []})
  public errorMessages!: string[]

  public get passedProps() {
    const props = {...this.$props}
    // @ts-ignore
    delete props.label
    // @ts-ignore
    delete props.success
    return props
  }

  public get errorColor() {
    if (this.errorFocused) {
      return 'red'
    }
    return 'primary'
  }

  public get errorFocused() {
    return !!this.errorMessages.length
  }
}
