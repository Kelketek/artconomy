<!--suppress XmlUnboundNsPrefix -->
<template>
  <div class="flex ac-editor">
    <v-row dense>
      <v-col
        v-if="previewMode"
        cols="12"
      >
        <v-row no-gutters>
          <ac-rendered
            :value="scratch"
            :classes="{'editor-preview': true, col: true}"
          />
        </v-row>
      </v-col>
      <v-col
        v-else
        cols="12"
      >
        <v-textarea
          v-bind="inputAttrs"
          ref="input"
          v-model="scratch"
          outlined
          :auto-grow="autoGrow"
          :error-messages="errorMessages"
        />
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <div class="flex-shrink-1">
            <v-tooltip
              top
              aria-label="Preview mode tooltip"
            >
              <template #activator="{ props }">
                <v-btn
                  size="small"
                  v-bind="props"
                  class="preview-mode-toggle"
                  :icon="previewMode ? 'mdi-eye-off' : 'mdi-eye'"
                  :class="{weakened: disabled}"
                  color="grey-darken-4"
                  :aria-label="`Preview mode ${previewMode ? 'on' : 'off'}`"
                  @click="previewMode = !previewMode"
                >
                  <v-icon
                    v-if="previewMode"
                    size="x-large"
                    :icon="mdiEyeOff"
                  />
                  <v-icon
                    v-else
                    :icon="mdiEye"
                    size="x-large"
                  />
                </v-btn>
              </template>
              <span>Preview</span>
            </v-tooltip>
          </div>
          <div class="flex-shrink-1 mx-2">
            <v-tooltip
              top
              aria-label="Tooltip for Formatting help button"
            >
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  :class="{weakened: disabled}"
                  size="small"
                  icon
                  color="blue"
                  aria-label="Formatting help"
                  @click="store.commit('setMarkdownHelp', true)"
                >
                  <v-icon
                    size="x-large"
                    :icon="mdiHelpCircle"
                  />
                </v-btn>
              </template>
              <span>Formatting help</span>
            </v-tooltip>
          </div>
          <div class="flex-grow-1" />
          <slot name="actions">
            <div class="flex-shrink-1">
              <v-row dense>
                <v-spacer />
                <slot
                  name="pre-actions"
                  :disabled="disabled"
                />
                <v-col class="shrink">
                  <v-tooltip
                    v-if="saved && saveIndicator"
                    top
                    aria-label="Tooltip for save indicator"
                  >
                    <template #activator="{ props }">
                      <!-- Using a button here so the two elements are aligned. -->
                      <v-btn
                        v-bind="props"
                        variant="plain"
                        icon
                        size="small"
                        class="save-indicator"
                        :ripple="false"
                        tabindex="-1"
                        :disabled="disabled"
                        aria-label="Saved."
                        @click.stop="() => {}"
                      >
                        <v-icon
                          color="green"
                          size="x-large"
                          class="save-indicator"
                          :icon="mdiCheckCircle"
                        />
                      </v-btn>
                    </template>
                    <span>Saved</span>
                  </v-tooltip>
                  <v-tooltip
                    v-else-if="saveIndicator"
                    top
                  >
                    <template #activator="{ props }">
                      <!-- Using a button here so the two elements are aligned. -->
                      <v-btn
                        v-bind="props"
                        variant="plain"
                        icon
                        size="small"
                        class="save-indicator"
                        :ripple="false"
                        tabindex="-1"
                        :disabled="disabled"
                        aria-label="Unsaved."
                        @click.stop="() => {}"
                      >
                        <v-icon
                          color="yellow"
                          size="x-large"
                          class="save-indicator"
                          :icon="mdiAlert"
                        />
                      </v-btn>
                    </template>
                    <span>Unsaved</span>
                  </v-tooltip>
                </v-col>
                <v-col
                  v-if="!autoSave"
                  class="shrink"
                >
                  <v-tooltip top>
                    <template #activator="{ props }">
                      <v-btn
                        v-bind="props"
                        :disabled="saved || disabled"
                        color="black"
                        icon
                        size="small"
                        @click="save"
                        class="save-button"
                        aria-label="Needs saving."
                      >
                        <v-icon
                          color="yellow"
                          :icon="mdiContentSave"
                        />
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

<script setup lang="ts">
import AcRendered from '@/components/wrappers/AcRendered.ts'
import {computed, ref, useAttrs, watch} from 'vue'
import {mdiEyeOff, mdiEye, mdiHelpCircle, mdiCheckCircle, mdiAlert, mdiContentSave} from '@mdi/js'
import {useRoute} from 'vue-router'
import {VTextarea} from 'vuetify/lib/components/VTextarea/index.mjs'
import {ArtState} from '@/store/artState.ts'
import {useStore} from 'vuex'


const props = withDefaults(defineProps<{
  modelValue: string,
  autoSave?: boolean,
  saveComparison?: string,
  autoGrow?: boolean,
  saveIndicator?: boolean,
  disabled?: boolean,
  errorMessages?: string[],
}>(), {
  autoSave: true,
  autoGrow: true,
  saveIndicator: true,
  disabled: false,
  errorMessages: () => [],
})
const route = useRoute()
const emit = defineEmits<{'update:modelValue': [string]}>()
const extraAttrs = useAttrs()

const input = ref<null|VTextarea>()
const previewMode = ref(false)
const scratch = ref(props.modelValue)
const store = useStore<ArtState>()
const save = () => emit('update:modelValue', scratch.value)

const inputAttrs = computed(() => {
  const attrs = {...extraAttrs}
  attrs.disabled = props.disabled
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
})

const saved = computed(() => {
  if (props.saveComparison === undefined) {
    return false
  }
  return props.saveComparison.trim() === scratch.value.trim()
})

const triggerResize = () => {
  // Only reliable way to trigger a resize is to tell the internal text element that an input event has occurred.
  if (!input.value) {
    return
  }
  input.value.querySelector('textarea')?.dispatchEvent(new Event('input'))
}

// Hacky workaround for v-show. Use the same boolean for v-show as for this to force a recalculation when
// changed.
watch(() => props.autoGrow, triggerResize)
watch(() => route.query.editing, triggerResize)
watch(scratch, () => {
  if (props.autoSave) {
    save()
  }
})
watch(() => props.modelValue, (val) => {
  if (props.autoSave) {
    scratch.value = val
  }
})
// Used in tests
defineExpose({emit, scratch})
</script>

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
