import QRCode from 'qrcode'
import {h, watch, ref, defineComponent} from 'vue'

export default defineComponent({
  props: {data: {type: String, required: true}},
  setup: (props) => {
    const innerHtml = ref('')
    watch(() => props.data, (value: string) => {
      QRCode.toString(value, {}, (err: Error | null | undefined, str: string) => {
        if (err) {
          console.error(err)
          innerHtml.value = ''
        }
        innerHtml.value = str
      })
    }, {immediate: true})
    return () => {
      return h('div', {class: 'qrcode', innerHTML: innerHtml.value})
    }
  }
})
