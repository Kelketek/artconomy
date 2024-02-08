import {h, resolveComponent} from 'vue'
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {FieldController} from '@/store/forms/field-controller.ts'
import AcUserSelect from '@/components/fields/AcUserSelect.vue'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcRatingField from '@/components/fields/AcRatingField.vue'
import AcUppyFile from '@/components/fields/AcUppyFile.vue'
import AcCharacterSelect from '@/components/fields/AcCharacterSelect.vue'
import AcPriceField from '@/components/fields/AcPriceField.vue'
import AcProductSelect from '@/components/fields/AcProductSelect.vue'
import AcCheckbox from '@/components/fields/AcCheckbox.vue'
import AcCaptchaField from '@/components/fields/AcCaptchaField.vue'
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {VSwitch} from 'vuetify/lib/components/VSwitch/index.mjs'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {VSlider} from 'vuetify/lib/components/VSlider/index.mjs'
import {VSelect} from 'vuetify/lib/components/VSelect/index.mjs'
import {VRadio} from 'vuetify/lib/components/VRadio/index.mjs'

const canonicalFields = ['input', 'button', 'textarea', 'select']

// Any components that might be used as a field and which aren't in Vuetify must be added here to resolve.
@Component({
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
    VRadio: VRadio.default,
  },
})
class AcBoundField extends Vue {
  @Prop({default: 'v-text-field'})
  public fieldType!: string

  @Prop()
  public fieldId!: string | undefined

  @Prop({required: true})
  public field!: FieldController

  public get attrs() {
    // We don't really know which keys are props and which are attrs. That's for the child component to decide, for the
    // most part. Here, we try to make our best guess and send almost everything except for things we know Vuetify
    // will complain about, since all, or nearly all, of our inputs are based on Vuetify components.
    let base: Record<string, any>
    if (canonicalFields.indexOf(this.fieldType) === -1) {
      base = {...this.field.bind}
    } else {
      base = {...this.field.rawBind}
    }
    if (this.fieldId) {
      base.id = this.fieldId
    }
    return {
      ...base,
      ref: 'input', ...this.$attrs,
    }
  }

  public render() {
    return h(resolveComponent(this.fieldType), {
      ...this.attrs,
    }, this.$slots)
  }
}

export default toNative(AcBoundField)
