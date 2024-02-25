import {h, resolveComponent, defineAsyncComponent, defineComponent, useSlots, useAttrs, computed} from 'vue'
import {FieldController} from '@/store/forms/field-controller.ts'
const AcUserSelect = defineAsyncComponent(() => import('@/components/fields/AcUserSelect.vue'))
const AcEditor = defineAsyncComponent(() => import('@/components/fields/AcEditor.vue'))
const AcTagField = defineAsyncComponent(() => import('@/components/fields/AcTagField.vue'))
const AcRatingField = defineAsyncComponent(() => import('@/components/fields/AcRatingField.vue'))
const AcUppyFile = defineAsyncComponent(() => import('@/components/fields/AcUppyFile.vue'))
const AcCharacterSelect = defineAsyncComponent(() => import('@/components/fields/AcCharacterSelect.vue'))
const AcPriceField = defineAsyncComponent(() => import('@/components/fields/AcPriceField.vue'))
const AcProductSelect = defineAsyncComponent(() => import('@/components/fields/AcProductSelect.vue'))
const AcCheckbox = defineAsyncComponent(() => import('@/components/fields/AcCheckbox.vue'))
const AcCaptchaField = defineAsyncComponent(() => import('@/components/fields/AcCaptchaField.vue'))
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {VSwitch} from 'vuetify/lib/components/VSwitch/index.mjs'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {VSlider} from 'vuetify/lib/components/VSlider/index.mjs'
import {VSelect} from 'vuetify/lib/components/VSelect/index.mjs'
import {VRadio as BaseVRadio} from 'vuetify/lib/components/VRadio/index.mjs'

const VRadio = BaseVRadio.default

const canonicalFields = ['input', 'button', 'textarea', 'select']

export default defineComponent({
  components: {
    AcUserSelect,
    AcEditor,
    AcTagField,
    AcRatingField,
    AcUppyFile,
    AcCharacterSelect,
    AcPriceField,
    AcProductSelect,
    AcCheckbox,
    AcCaptchaField,
    VTextField,
    VSwitch,
    VCheckbox,
    VAutocomplete,
    VSlider,
    VSelect,
    VRadio,
  },
  props: {
    fieldType: {
      default: 'v-text-field',
      type: String,
    },
    fieldId: {
      required: false,
      type: String,
    },
    field: {
      type: FieldController,
      required: true,
    }
  },
  setup: (props) => {
    const slots = useSlots()
    const passedAttrs = useAttrs()
    const attrs = computed(() => {
      // We don't really know which keys are props and which are attrs. That's for the child component to decide, for the
      // most part. Here, we try to make our best guess and send almost everything except for things we know Vuetify
      // will complain about, since all, or nearly all, of our inputs are based on Vuetify components.
      let base: Record<string, any>
      if (canonicalFields.indexOf(props.fieldType) === -1) {
        base = {...props.field.bind}
      } else {
        base = {...props.field.rawBind}
      }
      if (props.fieldId) {
        base.id = props.fieldId
      }
      return {
        ...base,
        ref: 'input', ...passedAttrs,
      }
    })
    return () => {
      return h(resolveComponent(props.fieldType), {
        ...attrs,
      }, slots)
    }
  }
})
