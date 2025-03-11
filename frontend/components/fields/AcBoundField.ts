import {computed, defineAsyncComponent, defineComponent, h, useAttrs, useSlots} from 'vue'
import type {Component} from 'vue'
import {FieldController} from '@/store/forms/field-controller.ts'
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {VSwitch} from 'vuetify/lib/components/VSwitch/index.mjs'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {VSlider} from 'vuetify/lib/components/VSlider/index.mjs'
import {VSelect} from 'vuetify/lib/components/VSelect/index.mjs'
import {VRadio as BaseVRadio} from 'vuetify/lib/components/VRadio/index.mjs'
import {transformComponentName} from '@/lib/lib.ts'
const VRadio = BaseVRadio.default

const canonicalFields = ['input', 'button', 'textarea', 'select']
const componentMapping: Record<string, Component> = {
  AcUserSelect: defineAsyncComponent(() => import('@/components/fields/AcUserSelect.vue')),
  AcEditor: defineAsyncComponent(() => import('@/components/fields/AcEditor.vue')),
  AcTagField: defineAsyncComponent(() => import('@/components/fields/AcTagField.vue')),
  AcRatingField: defineAsyncComponent(() => import('@/components/fields/AcRatingField.vue')),
  AcUppyFile: defineAsyncComponent(() => import('@/components/fields/AcUppyFile.vue')),
  AcCharacterSelect: defineAsyncComponent(() => import('@/components/fields/AcCharacterSelect.vue')),
  AcPriceField: defineAsyncComponent(() => import('@/components/fields/AcPriceField.vue')),
  AcProductSelect: defineAsyncComponent(() => import('@/components/fields/AcProductSelect.vue')),
  AcCheckbox: defineAsyncComponent(() => import('@/components/fields/AcCheckbox.vue')),
  AcCaptchaField: defineAsyncComponent(() => import('@/components/fields/AcCaptchaField.vue')),
  VTextField,
  VSwitch,
  VCheckbox,
  VAutocomplete,
  VSlider,
  VSelect,
  VRadio,
}

export default defineComponent({
  props: {
    fieldType: {
      default: 'v-text-field',
      type: String,
    },
    fieldId: {
      required: false,
      type: String,
      default: '',
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
      return h(componentMapping[transformComponentName(props.fieldType)], {
        ...attrs.value,
      }, slots)
    }
  }
})
