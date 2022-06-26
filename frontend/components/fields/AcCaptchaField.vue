<template>
  <v-input v-bind="$props" class="mt-4">
    <v-col class="text-center" >
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
import Vue from 'vue'
import VueHcaptcha from '@hcaptcha/vue-hcaptcha'
import Component from 'vue-class-component'

@Component({components: {VueHcaptcha}})
export default class AcCaptchaField extends Vue {
  public change(val: string) {
    this.$emit('input', val)
  }

  public reset() {
    this.change('')
  }

  // noinspection JSUnusedLocalSymbols,JSMethodCanBeStatic
  private get siteKey() {
    return window.RECAPTCHA_SITE_KEY || 'undefined'
  }
}
</script>
