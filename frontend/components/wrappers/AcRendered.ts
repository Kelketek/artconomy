import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import InlineAvatar from '@/components/InlineAvatar.vue'
import Formatting from '@/mixins/formatting'
import {compileToFunctions} from 'vue-template-compiler'
import {CreateElement} from 'vue'
import * as VGrid from 'vuetify/es5/components/VGrid'
import * as VToolbar from 'vuetify/es5/components/VToolbar'

@Component
export default class AcRendered extends mixins(Formatting) {
  @Prop({default: ''})
  public value!: string

  @Prop({default: 'v-col'})
  public tag!: string

  @Prop({default: false})
  public inline!: boolean

  @Prop({default: false})
  public truncate!: boolean|number

  @Prop({default: true})
  public showMore!: boolean

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
    const self = this
    return {
      components: {InlineAvatar, ...VGrid, ...VToolbar},
      data() {
        return {showMore: self.showMore}
      },
      render: compileToFunctions(this.dynamicTemplate).render,
    }
  }

  public get availableText(): string {
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
    return '<v-toolbar v-if="showMore" class="read-more-bar" dense @click="$parent.more=true" color="black">' +
      '<v-col class="text-center"><strong>Read More</strong></v-col>' +
      '</v-toolbar>'
  }
}
