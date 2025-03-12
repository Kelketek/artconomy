<template>
  <v-input v-bind="attributes" class="mt-4">
    <v-col class="text-center">
      <div style="display: inline-block">
        <vue-hcaptcha
          ref="recaptcha"
          :sitekey="siteKey"
          theme="dark"
          @verify="change"
          @expired="reset"
        />
      </div>
    </v-col>
  </v-input>
</template>

<script setup lang="ts">
import VueHcaptcha from "./hcaptcha/VueHcaptcha.vue"
import { computed, useAttrs } from "vue"

const attributes = useAttrs()
const emit = defineEmits<{ "update:modelValue": [string] }>()

const change = (val: string) => {
  emit("update:modelValue", val)
}

const reset = () => {
  change("")
}

const siteKey = computed(() => window.RECAPTCHA_SITE_KEY || "undefined")
</script>
