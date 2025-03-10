<template>
  <v-row
    ref="root"
    class="form-container"
    no-gutters
  >
    <div
      v-if="sending"
      class="loading-overlay"
    >
      <v-progress-circular
        v-if="showSpinner"
        indeterminate
        :size="70"
        :width="7"
        color="purple"
      />
    </div>
    <v-col
      :class="{'form-sending': sending}"
      cols="12"
    >
      <slot />
    </v-col>
    <template
      v-for="(error, index) in savedErrors"
      :key="index"
    >
      <v-col cols="12">
        <v-alert
          :key="error"
          :value="true"
          type="error"
          closable
          @update:model-value="(val) => {toggleError(val, index)}"
        >
          {{ error }}
        </v-alert>
      </v-col>
    </template>
  </v-row>
</template>

<script setup lang="ts">
import {nextTick, onMounted, ref, watch} from 'vue'

const props = withDefaults(
    defineProps<{sending?: boolean, errors?: string[], showSpinner?: boolean}>(),
    {
      sending: false,
      errors: () => [],
      showSpinner: true,
    }
)

const savedErrors = ref<string[]>([])

const toggleError = (val: boolean, index: number) => {
  if (val) {
    return
  }
  savedErrors.value.splice(index, 1)
}

watch(() => props.errors, (val: string[]) => {
  if (!Array.isArray(val)) {
    return
  }
  savedErrors.value = [...val]
})

const root = ref<Element|null>(null)

// Needed for tests.
defineExpose(props)

onMounted(() => {
  nextTick(() => {
    window._paq.push(['FormAnalytics::scanForForms', root.value!.outerHTML])
  })
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0;
  right: 0;
  height: 100%;
  width: 100%;
  z-index: 1;
  vertical-align: center;
  text-align: center;
}

.form-container {
  position: relative;
}

.form-sending {
  opacity: .25;
}

.error-right {
  float: right;
  display: inline-block
}
</style>
