import Vue, {CreateElement} from 'vue'
import {Prop} from 'vue-property-decorator'
import {FieldController} from '@/store/forms/field-controller'
import Component from 'vue-class-component'
import AcUserSelect from '@/components/fields/AcUserSelect.vue'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcRatingField from '@/components/fields/AcRatingField.vue'
import AcUppyFile from '@/components/fields/AcUppyFile.vue'
import AcCharacterSelect from '@/components/fields/AcCharacterSelect.vue'
import AcPriceField from '@/components/fields/AcPriceField.vue'
import AcProductSelect from '@/components/fields/AcProductSelect.vue'
import * as VCheckbox from 'vuetify/es5/components/VCheckbox'
import * as VSwitch from 'vuetify/es5/components/VSwitch'
import * as VTextField from 'vuetify/es5/components/VTextField'
import * as VAutocomplete from 'vuetify/es5/components/VAutocomplete'
import * as VSlider from 'vuetify/es5/components/VSlider'

// Any components that might be used as a field and which aren't in Vuetify must be added here to resolve.
@Component({components: {
  AcUserSelect,
  AcEditor,
  AcTagField,
  AcRatingField,
  AcUppyFile,
  AcCharacterSelect,
  AcPriceField,
  AcProductSelect,
  ...VTextField,
  ...VSwitch,
  ...VCheckbox,
  ...VAutocomplete,
  ...VSlider,
}})
export default class AcBoundField extends Vue {
  @Prop({default: 'v-text-field'})
  public fieldType!: string
  @Prop({required: true})
  public field!: FieldController

  public get binds() {
    const base = {...this.field.bind, ref: 'input'}
    return {...base, ...this.$attrs}
  }
  public get listeners() {
    const base = {...this.field.on}
    return {...base, ...this.$listeners}
  }
  public get attrs() {
    // We don't really know which keys are props and which are attrs. That's for the child component to decide, for the
    // most part. Here, we try to make our best guess and send almost everything except for things we know Vuetify
    // will complain about, since all, or nearly all, of our inputs are based on Vuetify components.
    const attrs = {...this.binds}
    delete attrs.value
    delete attrs.disabled
    return attrs
  }
  public render(h: CreateElement) {
    const children = Object.entries(this.$slots).map(([key, value]) => {
      // @ts-ignore
      return h('template', {slot: key}, [value])
    })
    return h(this.fieldType, {
      props: this.binds,
      on: this.listeners,
      scopedSlots: this.$scopedSlots,
      attrs: this.attrs,
      // @ts-ignore
    }, children)
  }
}
