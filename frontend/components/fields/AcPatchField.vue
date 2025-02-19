<template>
  <component :is="fieldComponent" v-bind="inputAttrs" v-model="scratch" v-if="(patcher.loaded || patcher.model)"
             @keydown.enter="enterHandler" class="patch-field">
    <template v-for="(_, name) in slots" #[name]>
      <slot :name="name"/>
    </template>
    <template #append>
      <div v-if="!handlesSaving">
        <v-tooltip v-if="saved && saveIndicator" text="Saved" location="top">
          <template v-slot:activator="{ props }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn size="x-small" v-bind="props" icon variant="plain" density="compact" class="save-indicator" @click.stop="() => {}"
                   :ripple="false" tabindex="-1">
              <v-icon size="x-small" color="green" class="save-indicator" :icon="mdiCheckCircle"/>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip v-else-if="saveIndicator" text="Unsaved" location="top">
          <template v-slot:activator="{ props }">
            <!-- Using a button here so the two elements are aligned. -->
            <v-btn v-bind="props" size="x-small" icon variant="plain" density="compact" class="save-indicator" @click.stop="() => {}"
                   :ripple="false" tabindex="-1" :disabled="disabled">
              <v-icon size="x-small" color="yellow" class="save-indicator" :icon="mdiAlert"/>
            </v-btn>
          </template>
        </v-tooltip>
        <v-tooltip v-if="!autoSave" text="Save" location="top">
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" @click="save" :disabled="saved || disabled" icon variant="plain" color="black"
                   class="save-button">
              <v-icon color="yellow" :icon="mdiContentSave"/>
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

<script setup lang="ts">
import {toValue, defineAsyncComponent, computed, useAttrs, ref, watch, useSlots} from 'vue'
import type {Component} from 'vue'
import {Patch} from '@/store/singles/patcher.ts'
import deepEqual from 'fast-deep-equal'
import {useTheme} from 'vuetify'
import {VCheckbox} from 'vuetify/lib/components/VCheckbox/index.mjs'
import {VSwitch} from 'vuetify/lib/components/VSwitch/index.mjs'
import {VTextField} from 'vuetify/lib/components/VTextField/index.mjs'
import {VAutocomplete} from 'vuetify/lib/components/VAutocomplete/index.mjs'
import {VSlider} from 'vuetify/lib/components/VSlider/index.mjs'
import {VSelect} from 'vuetify/lib/components/VSelect/index.mjs'
import {transformComponentName} from '@/lib/lib.ts'
import {mdiAlert, mdiCheckCircle, mdiContentSave} from '@mdi/js'

const componentMap: Record<string, Component> = {
  AcEditor: defineAsyncComponent(() => import('@/components/fields/AcEditor.vue')),
  AcTagField: defineAsyncComponent(() => import('@/components/fields/AcTagField.vue')),
  AcRatingField: defineAsyncComponent(() => import('@/components/fields/AcRatingField.vue')),
  AcUppyFile: defineAsyncComponent(() => import('@/components/fields/AcUppyFile.vue')),
  AcSubmissionSelect: defineAsyncComponent(() => import('@/components/fields/AcSubmissionSelect.vue')),
  AcBankToggle: defineAsyncComponent(() => import('@/components/fields/AcBankToggle.vue')),
  AcPriceField: defineAsyncComponent(() => import('@/components/fields/AcPriceField.vue')),
  AcStarField: defineAsyncComponent(() => import('@/components/fields/AcStarField.vue')),
  AcBirthdayField: defineAsyncComponent(() => import('@/components/fields/AcBirthdayField.vue')),
  AcCheckbox: defineAsyncComponent(() => import('@/components/fields/AcCheckbox.vue')),
  AcColorPrepend: defineAsyncComponent(() => import('@/components/fields/AcColorPrepend.vue')),
  VCheckbox,
  VSwitch,
  VTextField,
  VAutocomplete,
  VSlider,
  VSelect,
}

declare interface PatchFieldProps {
  fieldType?: string,
  patcher: Patch,
  saveIndicator?: boolean,
  autoSave?: boolean,
  enterSave?: boolean,
  id?: string,
  instant?: boolean,
}

const props = withDefaults(defineProps<PatchFieldProps>(), {
  fieldType: 'v-text-field',
  saveIndicator: true,
  autoSave: true,
  enterSave: true,
  instant: false,
})

const fieldComponent = componentMap[transformComponentName(props.fieldType)]

const passedAttrs = useAttrs()
const theme = useTheme()
const slots = useSlots()

const disabled = computed(() => {
  return Boolean(passedAttrs.disabled || (!props.autoSave && toValue(props.patcher.patching)))
})

const handlesSaving = computed(() => {
  // May want to find a way to generalize this in the future.
  return props.fieldType === 'ac-editor'
})

const loading = computed(() => {
  if (props.autoSave) {
    return false
  }
  if (toValue(props.patcher.patching)) {
    return (theme.current.value.colors.secondary as any).base
  }
  return false
})

const scratch = ref<any>(props.patcher.model)

const saved = computed(() => {
  let result: boolean
  if (typeof scratch.value !== 'string') {
    result = deepEqual(scratch.value, props.patcher.rawValue)
    return result
  }
  if (typeof props.patcher.rawValue === 'number') {
    return parseFloat(scratch.value) === props.patcher.rawValue
  }
  if (typeof props.patcher.rawValue !== 'string') {
    // Can't be saved if it's not the same type.
    return false
  }
  result = props.patcher.rawValue.trim() === scratch.value.trim()
  return result
})

const save = () => {
  if (!saved.value) {
    props.patcher.setValue(scratch.value)
  }
}

const inputAttrs = computed(() => {
  const attrs: any = {...passedAttrs}
  delete attrs.value
  delete attrs.modelValue
  attrs.errorMessages = toValue(props.patcher.errors)
  attrs.disabled = disabled.value
  attrs.loading = loading.value
  attrs.id = props.id
  if (handlesSaving.value) {
    attrs.autoSave = props.autoSave
    attrs.saveIndicator = props.saveIndicator
    attrs.saveComparison = props.patcher.rawValue
  }
  return attrs
})

watch(scratch, () => {
  if (props.autoSave || handlesSaving.value) {
    save()
  }
})

watch(() => props.patcher.model, (val: any) => {
  if (processInstantly()) {
    return
  }
  if (props.autoSave || handlesSaving.value) {
    scratch.value = val
  }
})

watch(() => props.patcher.rawValue, (val: any) => {
  if (!processInstantly()) {
    return
  }
  scratch.value = val
})

watch(() => props.patcher.cached, (val: any) => {
  // A synced handler is modifying our value.
  scratch.value = val
})

watch(saved, (val: boolean) => {
  if (val) {
    const patcher = props.patcher
    patcher.errors.value = []
  }
})

const enterHandler = () => {
  if (!props.enterSave) {
    return
  }
  save()
}

// document.hasFocus() isn't reactive, so this must be a function call.
const processInstantly = () => {
  return props.instant || !document.hasFocus()
}
</script>
