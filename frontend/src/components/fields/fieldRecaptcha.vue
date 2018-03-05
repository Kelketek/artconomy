<template>
  <div class="captcha-wrapper" :class="{'error--text': errors.length}">
    <vue-recaptcha
        :sitekey="schema.siteKey"
        ref="recaptcha"
        @verify="onVerify"
        @expired="onExpired"
        theme="dark"
    />
    <div v-if="schema.hint" class="input-group__messages input-group__hint">{{hint}}</div>
    <div v-if="errors.length" class="input-group__messages input-group__error">{{errors.join(', ')}}</div>
  </div>
</template>

<style scoped>
  .captcha-wrapper {
    display: inline-block;
  }
</style>

<script>
  import { abstractField } from 'vue-form-generator'
  import VueRecaptcha from 'vue-recaptcha'
  import { EventBus } from '../../lib'
  import materialField from './materialField'

  export default {
    components: {VueRecaptcha},
    name: 'fieldRecaptcha',
    mixins: [ abstractField, materialField ],
    methods: {
      onVerify: function (response) {
        this.value = response
        this.$emit('input', response)
      },
      onExpired: function () {
        this.resetRecaptcha()
      },
      resetRecaptcha () {
        this.value = ''
        this.$refs.recaptcha.reset() // Direct call reset method
      }
    },
    created () {
      EventBus.$on('form-failure', this.resetRecaptcha)
    },
    destroyed () {
      EventBus.$off('form-failure', this.resetRecaptcha)
    }
  }
</script>