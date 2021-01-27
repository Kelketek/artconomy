/**
 * AcRendered.ts
 *
 * This component renders markdown conveniently with truncation by default.
 *
 * We used to pass all of the markdown over to Vue's internal templating system, but it ballooned the size of the
 * file users must download. It has now been augmented with a series of manual rendering hacks to make it no longer
 * necessary to include the full template compiler.
 */
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Formatting from '@/mixins/formatting'
import {CreateElement} from 'vue'
import {genId} from '@/lib/lib'

/* istanbul ignore else */
// @ts-ignore
if (!window.renderAnchors) {
  // @ts-ignore
  window.renderAnchors = {}
}

@Component
export default class AcRendered extends mixins(Formatting) {
  @Prop({default: ''})
  public value!: string

  @Prop({default: 'div'})
  public tag!: string

  @Prop({default: () => ({col: true})})
  public classes!: {[key: string]: boolean}

  @Prop({default: false})
  public inline!: boolean

  @Prop({default: false})
  public truncate!: boolean|number

  @Prop({default: true})
  public showMore!: boolean

  public more = false

  public refId = genId()

  public get rendered() {
    if (this.inline) {
      return this.mdRenderInline(this.availableText)
    } else {
      return this.mdRender(this.availableText)
    }
  }

  public render(h: CreateElement) {
    return h(this.tag, {
      domProps: {
        innerHTML: this.rendered + this.readMore,
      },
      class: this.classes,
    })
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
    if ((!this.truncated) || !this.showMore) {
      return ''
    }
    return (
      `<header class="read-more-bar v-sheet theme--dark v-toolbar v-toolbar--dense black"
        onclick="window.renderAnchors['${this.refId}'].more = true"
      >` +
        '<div class="v-toolbar__content" style="height: 48px;">' +
          '<div class="text-center col">' +
            '<strong>Read More</strong>' +
          '</div>' +
        '</div>' +
      '</header>'
    )
  }

  // We need a way to reference this object from our ad-hoc js calls.
  public created() {
    // @ts-ignore
    window.renderAnchors[this.refId] = this
  }

  public destroy() {
    // Can't test this circuit through Jest for some reason.
    /* istanbul ignore next */
    // @ts-ignore
    delete window.renderAnchors[this.refId]
  }
}
