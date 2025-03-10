<template>
  <v-dialog
    ref="dialog"
    v-model="toggle"
    :fullscreen="fullscreen"
    :transition="transition"
    :persistent="persistent"
    :scrollable="true"
    :eager="eager"
    :width="width"
    :attach="modalTarget"
  >
    <v-card :id="id">
      <div v-if="smAndDown">
        <v-toolbar
          dark
          color="secondary"
        >
          <v-btn
            variant="plain"
            dark
            class="dialog-closer"
            @click="toggle = false"
          >
            <v-icon :icon="mdiClose" />
          </v-btn>
          <v-toolbar-title>{{ title }}</v-toolbar-title>
          <v-spacer />
          <slot name="top-buttons">
            <v-toolbar-items v-if="smAndDown">
              <v-btn
                variant="text"
                :disabled="disabled"
                @click.prevent="reSend"
              >
                {{ submitText }}
              </v-btn>
            </v-toolbar-items>
          </slot>
        </v-toolbar>
      </div>
      <v-toolbar
        v-else
        flat
        dark
        color="secondary"
        dense
      >
        <v-toolbar-title>{{ title }}</v-toolbar-title>
        <v-spacer />
        <v-btn
          icon
          dark
          class="dialog-closer"
          @click="toggle = false"
        >
          <v-icon :icon="mdiClose" />
        </v-btn>
      </v-toolbar>
      <v-card-text
        class="scrollableText"
        :class="{'pa-0': fluid}"
      >
        <ac-form @submit.prevent="reSend">
          <v-container class="pa-0">
            <slot name="header" />
          </v-container>
          <ac-form-container
            :errors="errors"
            :sending="sending"
          >
            <slot />
          </ac-form-container>
          <slot name="footer" />
          <slot
            name="bottom-buttons"
            :show-submit="showSubmit"
          >
            <v-card-actions
              row
              wrap
              class="hidden-sm-and-down"
            >
              <v-spacer />
              <v-btn
                variant="flat"
                @click="toggle=false"
              >
                {{ cancelText }}
              </v-btn>
              <v-btn
                v-if="showSubmit"
                variant="flat"
                color="primary"
                type="submit"
                :disabled="disabled"
                class="dialog-submit"
              >
                {{
                  submitText
                }}
              </v-btn>
            </v-card-actions>
          </slot>
        </ac-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import AcFormContainer from './AcFormContainer.vue'
import {defaultDialogProps, DialogProps, useDialog} from '@/mixins/dialog.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import {mdiClose} from '@mdi/js'
import {nextTick, watch} from 'vue'
import {useTargets} from '@/plugins/targets.ts'
import {useDisplay} from 'vuetify'
import {genId} from '@/lib/lib.ts'

declare interface AcFormDialogProps {
  sending?: boolean,
  disabled?: boolean,
  errors?: string[],
  submitText?: string,
  cancelText?: string,
  title?: string,
  id?: string,
  fluid?: boolean,
  eager?: boolean,
  showSubmit?: boolean,
}

const props = withDefaults(
  defineProps<DialogProps & AcFormDialogProps>(),
  {
    ...defaultDialogProps(),
    submitText: 'Submit',
    cancelText: 'Cancel',
    title: '',
    fluid: false,
    eager: false,
    showSubmit: true,
    disabled: false,
    sending: false,
    id: () => genId(),
    errors: () => [],
  },
)

const {modalTarget} = useTargets()

const {smAndDown} = useDisplay()

const emit = defineEmits<{'submit': [SubmitEvent], 'update:modelValue': [boolean]}>()

const {toggle, width, fullscreen, transition} = useDialog(props, emit)

const reSend = (event: SubmitEvent) => {
  emit('submit', event)
}

watch(() => props.modelValue, (value: boolean) => {
  if (!value) {
    return
  }
  nextTick(() => {
    const element = document.querySelector(`#${props.id} input[autofocus]`) as HTMLElement
    if (!element) {
      return
    }
    element.focus()
  })
})
</script>

<style scoped>
.hidden {
  display: none;
}
</style>
