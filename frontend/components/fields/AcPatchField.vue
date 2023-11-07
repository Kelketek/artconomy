<!--suppress XmlUnboundNsPrefix -->
<template>
  <component :is="fieldType" v-bind="inputAttrs" v-model="scratch" v-if="(patcher.loaded || patcher.model)"
             @keydown.enter="enterHandler" class="patch-field">
    <template v-for="(_, name) in $slots" #[name]>
      <slot :name="name"/>
    </template>
    <template #append>
      <div v-if="!handlesSaving">
        <v-tooltip v-if="saved && saveIndicator" text="Saved" location="top">
          <template v-slot:activator="{ props }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn size="x-small" v-bind="props" icon variant="plain" density="compact" class="save-indicator" @click.stop="() => {}"
                   :ripple="false" tabindex="-1">
              <v-icon size="x-small" color="green" class="save-indicator" icon="mdi-check-circle"/>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip v-else-if="saveIndicator" text="Unsaved" location="top">
          <template v-slot:activator="{ props }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn v-bind="props" size="x-small" icon variant="plain" density="compact" class="save-indicator" @click.stop="() => {}"
                   :ripple="false" tabindex="-1" :disabled="disabled">
              <v-icon size="x-small" color="yellow" class="save-indicator" icon="mdi-alert"/>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip v-if="!autoSave" text="Save" location="top">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" @click="save" :disabled="saved || disabled" icon variant="plain" color="black"
                   class="save-button">
              <v-icon color="yellow" icon="mdi-content-save"/>
            </v-btn>
          </template>
        </v-tooltip>
      </div>
    </template>
  </component>
</template>

<style lang="stylus">
.save-indicator {
  &.v-btn--active::before,
  &.v-btn:hover::before, &.v-btn:focus::before {
    background-color: unset;
  }
}
</style>

<script lang="ts">
import {toValue} from 'vue'
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'
import {Patch} from '@/store/singles/patcher'
import deepEqual from 'fast-deep-equal'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcRatingField from '@/components/fields/AcRatingField.vue'
import AcUppyFile from '@/components/fields/AcUppyFile.vue'
import AcSubmissionSelect from '@/components/fields/AcSubmissionSelect.vue'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import AcPriceField from '@/components/fields/AcPriceField.vue'
import AcStarField from '@/components/fields/AcStarField.vue'
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {VSwitch} from 'vuetify/lib/components/VSwitch/index.mjs'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {VSlider} from 'vuetify/lib/components/VSlider/index.mjs'
import {VSelect} from 'vuetify/lib/components/VSelect/index.mjs'
import AcBirthdayField from '@/components/fields/AcBirthdayField.vue'
import AcCheckbox from '@/components/fields/AcCheckbox.vue'

// @ts-ignore
@Component({
  components: {
    AcBirthdayField,
    AcStarField,
    AcPriceField,
    AcBankToggle,
    AcSubmissionSelect,
    AcUppyFile,
    AcRatingField,
    AcTagField,
    AcEditor,
    AcCheckbox,
    VTextField,
    VCheckbox,
    VSwitch,
    VAutocomplete,
    VSlider,
    VSelect,
  },
})
class AcPatchField extends Vue {
  @Prop({default: 'v-text-field'})
  public fieldType!: string

  @Prop({required: true})
  public patcher!: Patch

  @Prop({default: true})
  public saveIndicator!: boolean

  @Prop({default: true})
  public autoSave!: boolean

  @Prop({default: false})
  public enterSave!: boolean

  @Prop()
  public id!: string

  // This will update the field from upstream pushes instantly. You don't want this for text. You do for booleans.
  // For sanity between tabs, this is counted as true if the window is not focused either way.
  @Prop({default: false})
  public instant!: boolean

  public scratch: any = ''

  public created() {
    this.scratch = this.patcher.model
  }

  public save() {
    if (!this.saved) {
      this.patcher.setValue(this.scratch)
    }
  }

  @Watch('scratch')
  public watchScratch() {
    if (this.autoSave || this.handlesSaving) {
      this.save()
    }
  }

  @Watch('patcher.model')
  public watchModel(val: any) {
    if (this.processInstantly) {
      return
    }
    if (this.autoSave || this.handlesSaving) {
      this.scratch = val
    }
  }

  @Watch('patcher.rawValue')
  public watchRawValue(val: any) {
    if (!this.processInstantly) {
      return
    }
    this.scratch = val
  }

  @Watch('patcher.cached')
  public watchCache(val: any) {
    // A synced handler is modifying our value.
    this.scratch = val
  }

  @Watch('patcher.errors')
  public errorCheck(val: string[]) {
    if (val.length && !this.autoSave) {
      // When we have an error, our cache will still have the new value. We need to reset it so that our child
      // component knows we've still not saved what's upstream. Note: This is only for child components that handle
      // their own save events, such as the editor. Doing this on other components runs the risk of wiping out
      // the value the user set. To override this, set refresh to false.
      this.scratch = this.patcher.rawValue
    }
  }

  public enterHandler() {
    if (!this.enterSave) {
      return
    }
    this.save()
  }

  @Watch('saved')
  public clearErrorsIfSaved(val: boolean) {
    if (val) {
      this.patcher.errors.value = []
    }
  }

  public get saved() {
    let result: boolean
    if (typeof this.scratch !== 'string') {
      result = deepEqual(this.scratch, this.patcher.rawValue)
      return result
    }
    if (typeof this.patcher.rawValue === 'number') {
      return parseFloat(this.scratch) === this.patcher.rawValue
    }
    if (typeof this.patcher.rawValue !== 'string') {
      // Can't be saved if it's not the same type.
      return false
    }
    result = this.patcher.rawValue.trim() === this.scratch.trim()
    return result
  }

  public get disabled() {
    return Boolean(this.$attrs.disabled || (!this.autoSave && toValue(this.patcher.patching)))
  }

  public get processInstantly() {
    return this.instant || !document.hasFocus()
  }

  public get loading() {
    if (this.autoSave) {
      return false
    }
    if (toValue(this.patcher.patching)) {
      return (this.$vuetify.theme.current.colors.secondary as any).base
    }
    return false
  }

  public get handlesSaving() {
    // May want to find a way to generalize this in the future.
    return this.fieldType === 'ac-editor'
  }

  public get inputAttrs() {
    const attrs: any = {...this.$attrs}
    delete attrs.value
    delete attrs.modelValue
    attrs.errorMessages = toValue(this.patcher.errors)
    attrs.disabled = this.disabled
    attrs.loading = this.loading
    attrs.id = this.id
    if (this.handlesSaving) {
      attrs.autoSave = this.autoSave
      attrs.saveIndicator = this.saveIndicator
      attrs.saveComparison = this.patcher.rawValue
    }
    return attrs
  }
}

export default toNative(AcPatchField)
</script>
