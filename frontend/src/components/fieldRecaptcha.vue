<template>
  <vue-recaptcha
      :sitekey="schema.siteKey"
      ref="recaptcha"
      @verify="onVerify"
      @expired="onExpired"
  />
</template>

<script>
  import { abstractField } from 'vue-form-generator'
  import VueRecaptcha from 'vue-recaptcha'
  import { EventBus } from '../lib'

  export default {
    components: {VueRecaptcha},
    name: 'fieldRecaptcha',
    mixins: [ abstractField ],
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