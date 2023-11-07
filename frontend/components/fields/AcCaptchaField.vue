<template>
  <v-input v-bind="$props" class="mt-4">
    <v-col class="text-center">
      <div style="display: inline-block">
        <vue-hcaptcha
            :sitekey="siteKey"
            ref="recaptcha"
            @verify="change"
            @expired="reset"
            theme="dark"
        />
      </div>
    </v-col>
  </v-input>
</template>

<script lang="ts">
import VueHcaptcha from '@hcaptcha/vue3-hcaptcha'
import {Component, toNative, Vue} from 'vue-facing-decorator'

@Component({
  components: {VueHcaptcha},
  emits: ['update:modelValue'],
})
class AcCaptchaField extends Vue {
  public change(val: string) {
    this.$emit('update:modelValue', val)
  }

  public reset() {
    this.change('')
  }

  // noinspection JSUnusedLocalSymbols,JSMethodCanBeStatic
  public get siteKey() {
    return window.RECAPTCHA_SITE_KEY || 'undefined'
  }
}

export default toNative(AcCaptchaField)
</script>
