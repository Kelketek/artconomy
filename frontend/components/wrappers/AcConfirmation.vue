<!--suppress JSUnusedLocalSymbols -->
<template>
  <slot :on="on">
    <v-btn class="confirm-launch" variant="flat" @click="show"> Submit </v-btn>
  </slot>
  <v-dialog
    v-model="showModal"
    max-width="500px"
    :persistent="sending"
    :attach="modalTarget"
  >
    <v-card :class="cardClass">
      <v-toolbar flat dark color="secondary">
        <v-toolbar-title>
          <slot name="title"> Are you sure? </slot>
        </v-toolbar-title>
        <v-spacer />
        <v-btn icon dark class="dialog-closer" @click="showModal = false">
          <v-icon :icon="mdiClose" />
        </v-btn>
      </v-toolbar>
      <div v-if="sending" class="loading-overlay">
        <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
        />
      </div>
      <v-card-text :class="{ 'confirm-submitting': sending }">
        <slot name="confirmation-text"> This cannot be undone. </slot>
        <v-spacer />
      </v-card-text>
      <v-card-actions right :class="{ 'confirm-submitting': sending }">
        <v-spacer />
        <v-btn
          variant="flat"
          :disabled="sending"
          class="cancel-button"
          @click.stop="showModal = false"
        >
          <slot name="cancel-text"> Cancel </slot>
        </v-btn>
        <v-btn
          variant="flat"
          color="red"
          :disabled="sending"
          class="confirmation-button"
          @click.stop="submit"
        >
          <slot name="confirm-text"> Yes, I am sure. </slot>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { mdiClose } from "@mdi/js"
import { computed, ref } from "vue"
import { useTargets } from "@/plugins/targets.ts"

const props = defineProps<{
  action: () => Promise<unknown>
  cardClass?: string
}>()
const showModal = ref(false)
const sending = ref(false)
const { modalTarget } = useTargets()

const dismiss = () => {
  showModal.value = false
  sending.value = false
}

const show = (event: Event) => {
  event.stopPropagation()
  showModal.value = true
}

const submit = () => {
  sending.value = true
  props.action().finally(dismiss)
}

const on = computed(() => ({ click: show }))
</script>

<style>
.loading-overlay {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0;
  right: 0;
  height: 100%;
  width: 100%;
  vertical-align: center;
  text-align: center;
  z-index: 205;
}

/*noinspection ALL*/
.confirm-submitting {
  opacity: 0.4;
}
</style>
