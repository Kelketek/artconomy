import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import Formatting from '@/mixins/formatting'
import {compileToFunctions} from 'vue-template-compiler'
import {CreateElement} from 'vue'
import * as VGrid from 'vuetify/es5/components/VGrid'

@Component
export default class AcRendered extends mixins(Formatting) {
  @Prop()
  public value!: string
  @Prop({default: 'v-col'})
  public tag!: string
  @Prop({default: false})
  public inline!: boolean
  @Prop({default: false})
  public truncate!: boolean|number

  public more = false

  public get rendered() {
    if (this.inline) {
      return this.mdRenderInline(this.availableText)
    } else {
      return this.mdRender(this.availableText)
    }
  }

  public render(h: CreateElement) {
    return h(this.renderedComponent)
  }

  public get dynamicTemplate() {
    return `<${this.tag}>${this.rendered}${this.readMore}</${this.tag}>`
  }

  public get renderedComponent() {
    return {
      components: {AcAvatar, ...VGrid},
      render: compileToFunctions(this.dynamicTemplate).render,
    }
  }
  public get availableText() {
    if (this.more) {
      return this.value
    }
    let value = this.value || ''
    let truncateLength: number|undefined
    if (this.truncate) {
      if (typeof this.truncate === 'number') {
        truncateLength = this.truncate
      } else {
        truncateLength = 1000
      }
      value = this.truncateText(value, truncateLength)
    }
    return value
  }
  public get truncated() {
    return !(this.availableText === this.value)
  }
  public get readMore() {
    if (!this.truncated) {
      return ''
    }
    return '<v-toolbar class="read-more-bar" dense @click="$parent.more=true">' +
      '<v-col class="text-center"><strong>Read More</strong></v-col>' +
      '</v-toolbar>'
  }
}
