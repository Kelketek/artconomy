<!--suppress XmlUnboundNsPrefix -->
<template>
  <div class="flex ac-editor">
    <v-row dense>
      <v-col cols="12" v-if="previewMode">
        <v-row no-gutters>
          <ac-rendered :value="scratch" :classes="{'editor-preview': true, col: true}"/>
        </v-row>
      </v-col>
      <v-col cols="12" v-else>
        <v-textarea v-bind="inputAttrs" ref="input" v-model="scratch" outlined :auto-grow="autoGrow"
                    :error-messages="errorMessages"/>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <div class="flex-shrink-1">
            <v-tooltip top aria-label="Preview mode tooltip">
              <template v-slot:activator="{ props }">
                <v-btn size="small" v-bind="props" @click="previewMode = !previewMode" class="preview-mode-toggle"
                       :icon="previewMode ? 'mdi-eye-off' : 'mdi-eye'" :class="{weakened: disabled}"
                       color="grey-darken-4"
                       :aria-label="`Preview mode ${previewMode ? 'on' : 'off'}`"
                >
                  <v-icon v-if="previewMode" size="x-large" :icon="mdiEyeOff"/>
                  <v-icon v-else :icon="mdiEye" size="x-large"/>
                </v-btn>
              </template>
              <span>Preview</span>
            </v-tooltip>
          </div>
          <div class="flex-shrink-1 mx-2">
            <v-tooltip top aria-label="Tooltip for Formatting help button">
              <template v-slot:activator="{ props }">
                <v-btn v-bind="props" @click="$store.commit('setMarkdownHelp', true)" :class="{weakened: disabled}"
                       size="small" icon color="blue" aria-label="Formatting help">
                  <v-icon size="x-large" :icon="mdiHelpCircle"/>
                </v-btn>
              </template>
              <span>Formatting help</span>
            </v-tooltip>
          </div>
          <div class="flex-grow-1"/>
          <slot name="actions">
            <div class="flex-shrink-1">
              <v-row dense>
                <v-spacer/>
                <slot name="pre-actions" :disabled="disabled"/>
                <v-col class="shrink">
                  <v-tooltip top v-if="saved && saveIndicator" aria-label="Tooltip for save indicator">
                    <template v-slot:activator="{ props }">
                      <!-- Using a button here so the two elements are aligned. -->
                      <v-btn v-bind="props" variant="plain" icon size="small" class="save-indicator"
                             @click.stop="() => {}" :ripple="false" tabindex="-1" :disabled="disabled" aria-label="Saved.">
                        <v-icon color="green" size="x-large" class="save-indicator" :icon="mdiCheckCircle"/>
                      </v-btn>
                    </template>
                    <span>Saved</span>
                  </v-tooltip>
                  <v-tooltip top v-else-if="saveIndicator">
                    <template v-slot:activator="{ props }">
                      <!-- Using a button here so the two elements are aligned. -->
                      <v-btn v-bind="props" variant="plain" icon size="small" class="save-indicator"
                             @click.stop="() => {}" :ripple="false" tabindex="-1" :disabled="disabled" aria-label="Unsaved.">
                        <v-icon color="yellow" size="x-large" class="save-indicator" :icon="mdiAlert"/>
                      </v-btn>
                    </template>
                    <span>Unsaved</span>
                  </v-tooltip>
                </v-col>
                <v-col class="shrink" v-if="!autoSave">
                  <v-tooltip top>
                    <template v-slot:activator="{ props }">
                      <v-btn v-bind="props" @click="save" :disabled="saved || disabled" color="black" icon size="small"
                             class="save-button" aria-label="Needs saving.">
                        <v-icon color="yellow" :icon="mdiContentSave"/>
                      </v-btn>
                    </template>
                    <span>Save</span>
                  </v-tooltip>
                </v-col>
              </v-row>
            </div>
          </slot>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<style lang="stylus">
.save-indicator {
  &.v-btn--active::before,
  &.v-btn:hover::before, &.v-btn:focus::before {
    background-color: unset;
  }
}

.weakened {
  opacity: .25
}
</style>

<script lang="ts">
import {Component, Prop, toNative, Watch} from 'vue-facing-decorator'
import AcMarkdownExplanation from '@/components/fields/AcMarkdownExplination.vue'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import {ComponentPublicInstance} from 'vue'
import {ArtVue} from '@/lib/lib.ts'
import {mdiEyeOff, mdiEye, mdiHelpCircle, mdiCheckCircle, mdiAlert, mdiContentSave} from '@mdi/js'

@Component({
  components: {
    AcRendered,
    AcMarkdownExplanation,
  },
  emits: ['update:modelValue'],
})
class AcEditor extends ArtVue {
  @Prop({required: true})
  public modelValue!: string

  @Prop({default: true})
  public autoSave!: boolean

  @Prop({default: null})
  public saveComparison!: string | null

  @Prop({default: true})
  public autoGrow!: boolean

  @Prop({default: true})
  public saveIndicator!: boolean

  @Prop({default: false})
  public disabled!: boolean

  @Prop({default: () => []})
  public errorMessages!: string[]

  public previewMode = false

  public scratch: string = ''
  public mdiEyeOff = mdiEyeOff
  public mdiEye = mdiEye
  public mdiHelpCircle = mdiHelpCircle
  public mdiCheckCircle = mdiCheckCircle
  public mdiAlert = mdiAlert
  public mdiContentSave = mdiContentSave

  public created() {
    this.scratch = this.modelValue
  }

  public save() {
    this.$emit('update:modelValue', this.scratch)
  }

  @Watch('scratch')
  public watchScratch() {
    if (this.autoSave) {
      this.save()
    }
  }

  @Watch('modelValue')
  public watchValue(val: string) {
    if (this.autoSave) {
      this.scratch = val
    }
  }

  public triggerResize() {
    // Only reliable way to trigger a resize is to tell the internal text element that an input event has occurred.
    const inputElement = this.$refs.input as ComponentPublicInstance
    inputElement.$el.querySelector('textarea')!.dispatchEvent(new Event('input'))
  }

  @Watch('$route.query.editing')
  public editingResize(val: any) {
    // Most cases where we need to have a text area hidden, we use v-show, which makes calculation of field height
    // impossible.
    //
    // In those cases, watch for the editing flag to be flipped and resize if so.
    this.triggerResize()
  }

  @Watch('autoGrow')
  public autoGrowResize() {
    // Hacky workaround for v-show. Use the same boolean for v-show as for this to force a recalculation when
    // changed.
    this.triggerResize()
  }

  public get inputAttrs() {
    const attrs: any = {...this.$attrs}
    attrs.disabled = this.disabled
    delete attrs.value
    delete attrs.modelValue
    delete attrs.autoSave
    delete attrs.onInput
    delete attrs.onChange
    delete attrs.onBlur
    delete attrs['onUpdate:modelValue']
    if (attrs.id) {
      attrs['id'] += '__textarea'
    }
    return attrs
  }

  public get saved() {
    if (this.saveComparison === null) {
      return false
    }
    return this.saveComparison.trim() === this.scratch.trim()
  }
}

export default toNative(AcEditor)
</script>
