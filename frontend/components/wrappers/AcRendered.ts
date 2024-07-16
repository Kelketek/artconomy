/**
 * AcRendered.ts
 *
 * This component renders markdown conveniently with truncation by default.
 *
 * We used to pass all the markdown over to Vue's internal templating system, but it ballooned the size of the
 * file users must download. It has now been augmented with a series of manual rendering hacks to make it no longer
 * necessary to include the full template compiler.
 */
import {computed, defineComponent, h, PropType, ref, useSlots} from 'vue'
import {md} from '@/lib/markdown.ts'
import {truncateText} from '@/lib/otherFormatters.ts'

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

export default defineComponent({
  props: {
    value: {default: '', type: String},
    tag: {default: 'div', type: String},
    classes: {default: () => ({'v-col': true}), type: Object as PropType<{[key: string]: boolean}>},
    inline: {default: false, type: Boolean},
    truncate: {default: false, type: [Number, Boolean]},
    showMore: {default: true, type: Boolean},
  },
  setup: (props) => {
    const more = ref(false)
    const slots = useSlots()
    const availableText = computed(() => {
      if (more.value) {
        return props.value
      }
      let value = props.value || ''
      let truncateLength: number | undefined
      if (props.truncate) {
        if (typeof props.truncate === 'number') {
          truncateLength = props.truncate
        } else {
          truncateLength = 1000
        }
        value = truncateText(value, truncateLength)
      }
      return value
    })
    const truncated = computed(() => !(availableText.value === (props.value || '')))
    const rendered = computed(() => {
      let content: string
      if (props.inline) {
        content = md.renderInline(availableText.value)
      } else {
        content = md.render(availableText.value)
      }
      const elements = fromHTML(content, props.inline)
      if (props.inline) {
        const renderedTag = elements[0]
        return [h(renderedTag.tagName, {innerHTML: renderedTag.innerHTML})]
      }
      return elements.map((element) => h(element.tagName, {
        ...element.attributes,
        innerHTML: element.innerHTML,
      }))
    })
    const readMore = computed(() => {
      if ((!truncated.value) || !props.showMore) {
        return []
      }
      return [
        h('header', {
          class: 'read-more-bar v-toolbar v-toolbar--density-compact bg-black v-theme--dark v-locale--is-ltr',
          onClick: () => more.value = true,
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
    })
    return () => {
      if (!availableText.value && slots.empty) {
        return slots.empty()
      }
      if (props.inline) {
        return rendered.value[0]
      }
      return h(props.tag, {class: {'markdown-rendered': true, ...props.classes}}, [...rendered.value, ...readMore.value])
    }
  }
})
