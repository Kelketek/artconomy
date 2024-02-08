/**
 * AcRendered.ts
 *
 * This component renders markdown conveniently with truncation by default.
 *
 * We used to pass all the markdown over to Vue's internal templating system, but it ballooned the size of the
 * file users must download. It has now been augmented with a series of manual rendering hacks to make it no longer
 * necessary to include the full template compiler.
 */
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Formatting from '@/mixins/formatting.ts'
import {h} from 'vue'
import {genId} from '@/lib/lib.ts'

function fromHTML(html: string, inline: boolean) {
  // Adapted from: https://stackoverflow.com/a/35385518/927224
  // Process the HTML string.
  if (!html) return [document.createElement('span')]

  if (inline) {
    const span = document.createElement('span')
    span.innerHTML = html
    return [span]
  }
  // Then set up a new template element.
  const template = document.createElement('template')
  template.innerHTML = html
  return Array.from(template.content.children)
}

@Component
class AcRendered extends mixins(Formatting) {
  @Prop({default: ''})
  public value!: string

  @Prop({default: 'div'})
  public tag!: string

  @Prop({default: () => ({'v-col': true})})
  public classes!: { [key: string]: boolean }

  @Prop({default: false})
  public inline!: boolean

  @Prop({default: false})
  public truncate!: boolean | number

  @Prop({default: true})
  public showMore!: boolean

  public more = false

  public refId = genId()

  public get rendered() {
    let content: string
    if (this.inline) {
      content = this.mdRenderInline(this.availableText)
    } else {
      content = this.mdRender(this.availableText)
    }
    const elements = fromHTML(content, this.inline)
    if (this.inline) {
      const renderedTag = elements[0]
      return [h(renderedTag.tagName, {innerHTML: renderedTag.innerHTML})]
    }
    return elements.map((element) => h(element.tagName, {
      ...element.attributes,
      innerHTML: element.innerHTML,
    }))
  }

  public render() {
    if (!this.availableText && this.$slots.empty) {
      return this.$slots.empty()
    }
    const rendered = this.rendered
    if (this.inline) {
      return rendered[0]
    }
    return h(this.tag, {class: this.classes}, [...rendered, ...this.readMore])
  }

  public get availableText(): string {
    if (this.more) {
      return this.value
    }
    let value = this.value || ''
    let truncateLength: number | undefined
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
    return !(this.availableText === (this.value || ''))
  }

  public get readMore() {
    if ((!this.truncated) || !this.showMore) {
      return []
    }
    return [
      h('header', {
        class: 'read-more-bar v-toolbar v-toolbar--density-compact bg-black v-theme--dark v-locale--is-ltr',
        onClick: () => this.more = true,
      }, [
        h('div', {
          class: 'v-toolbar__content',
          style: 'height: 48px;',
        }, [
          h('div', {class: 'v-col text-center'}, [
            h('strong', ['Read More']),
          ]),
        ]),
      ]),
    ]
  }
}

export default toNative(AcRendered)
