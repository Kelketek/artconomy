import {Component, Prop} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'

@Component({emits: ['update:modelValue']})
export default class Dialog extends ArtVue {
  @Prop({default: false})
  public modelValue!: boolean

  @Prop({default: false})
  public large!: boolean

  @Prop({default: true})
  public persistent!: boolean

  /* istanbul ignore next */
  public get width() {
    switch (this.$vuetify.display.name) {
      // These top two should be ignored due to the fullscreen directive, but...
      case 'xs': return '100vw'
      case 'sm': return '100vw'
      case 'md': return '80vw'
      case 'lg': return this.large ? '80vw' : '60vw'
      case 'xl': return this.large ? '60vw' : '40vw'
    }
  }

  /* istanbul ignore next */
  public get transition() {
    if (this.$vuetify.display.smAndDown) {
      return 'dialog-bottom-transition'
    } else {
      return 'fade-transition'
    }
  }

  public get fullscreen() {
    return this.$vuetify.display.smAndDown
  }

  public get toggle() {
    return this.modelValue
  }

  public set toggle(value) {
    this.$emit('update:modelValue', value)
  }
}
