import {computed} from 'vue'
import {useDisplay} from 'vuetify'


declare interface DialogPropsResolved {
  modelValue: boolean,
  large: boolean,
  persistent: boolean,
  eager: boolean,
}

export type DialogProps = Partial<DialogPropsResolved>

export const defaultDialogProps = () => ({modelValue: false, large: false, persistent: true, eager: false})

export const useDialog = (props: DialogPropsResolved, emit: (evt: 'update:modelValue', args_0: boolean) => void) => {
  const toggle = computed({
    get: () => props.modelValue,
    set: (value: boolean) => {
      emit('update:modelValue', value)
    }
  })
  const display = useDisplay()
  const fullscreen = computed(() => display.smAndDown.value)
  const transition = computed(() => {
    if (display.smAndDown.value) {
      return 'dialog-bottom-transition'
    } else {
      return 'fade-transition'
    }
  })
  const width = computed(() => {
    switch (display.name.value) {
      // These top two should be ignored due to the fullscreen directive, but...
      case 'xs': return '100vw'
      case 'sm': return '100vw'
      case 'md': return '80vw'
      case 'lg': return props.large ? '80vw' : '60vw'
      case 'xl': return props.large ? '60vw' : '40vw'
    }
  })
  return {
    emit,
    toggle,
    width,
    fullscreen,
    transition,
  }
}
