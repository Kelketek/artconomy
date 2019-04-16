import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'

@Component
export default class Dialog extends Vue {
  @Prop({default: false})
  public value!: boolean
  @Prop({default: false})
  public large!: boolean
  @Prop({default: true})
  public persistent!: boolean
  @Prop({default: false})
  public lazy!: boolean

  /* istanbul ignore next */
  public get width() {
    switch (this.$vuetify.breakpoint.name) {
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
    if (this.$vuetify.breakpoint.smAndDown) {
      return 'dialog-bottom-transition'
    } else {
      return 'fade-transition'
    }
  }

  public get fullscreen() {
    return this.$vuetify.breakpoint.smAndDown
  }

  public get toggle() {
    return this.value
  }

  public set toggle(value) {
    this.$emit('input', value)
  }
}
