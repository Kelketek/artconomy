import {computed} from 'vue'


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
