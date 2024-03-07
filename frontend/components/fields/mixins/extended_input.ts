import {Component, Prop} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'
import {computed} from 'vue'

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

export interface ExtendedInputProps {
  label: string,
  errorMessages?: string[],
}

export const useExtendedInput = <T extends ExtendedInputProps>(props: T) => {
  const passedProps = computed(() => {
    const toPass = {...props} as ExtendedInputProps
    // @ts-ignore
    delete toPass.success
    // @ts-ignore
    delete toPass.label
    return props
  })
  const errorFocused = computed(() => {
    if (!props.errorMessages) {
      return 0
    }
    return props.errorMessages.length
  })
  const errorColor = computed(() => errorFocused.value ? 'red' : 'primary')
  return {
    passedProps,
    errorFocused,
    errorColor,
  }
}
