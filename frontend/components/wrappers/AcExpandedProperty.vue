<template>
  <v-dialog
    v-model="toggle"
    :width="width"
    :transition="transition"
    :fullscreen="fullscreen"
    :eager="eager"
    :attach="modalTarget"
  >
    <v-card tile>
      <v-toolbar flat dark color="secondary" :dense="display.mdAndUp.value">
        <v-toolbar-title>
          <slot name="title" />
        </v-toolbar-title>
        <v-spacer />
        <v-btn icon dark class="dialog-closer" @click="toggle = false">
          <v-icon :icon="mdiClose" />
        </v-btn>
      </v-toolbar>
      <ac-form @submit.prevent="toggle = false">
        <v-card-text class="scrollableText">
          <slot />
        </v-card-text>
        <v-card-actions>
          <slot name="actions">
            <v-spacer />
            <v-btn color="primary" variant="flat" type="submit"> Done </v-btn>
          </slot>
        </v-card-actions>
      </ac-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { defaultDialogProps, DialogProps, useDialog } from "@/mixins/dialog.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import { mdiClose } from "@mdi/js"
import { useTargets } from "@/plugins/targets.ts"
import { useDisplay } from "vuetify"

const props = withDefaults(defineProps<DialogProps>(), defaultDialogProps())
const emit = defineEmits<{ "update:modelValue": [boolean] }>()
const display = useDisplay()
const { modalTarget } = useTargets()
const { toggle, width, transition, fullscreen } = useDialog(props, emit)
</script>
