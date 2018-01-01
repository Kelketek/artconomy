<template>
  <div class="ac-action-container">
    <b-button v-if="button" :variant="variant" :disabled="isDisabled" :type="type" @click="performAction"><slot></slot></b-button>
    <div v-else class="ac-action-div" @click="performAction"><slot @click="performAction"></slot></div>
    <b-modal ref="confModal" v-if="confirm" ok_button_text="Yes, I am sure" @ok="submit">
      <slot name="confirmation-text">
        Are you sure?
      </slot>
    </b-modal>
  </div>
</template>

<script>
  import { artCall } from '../lib'

  export default {
    name: 'ac-action',
    props: {
      confirm: {
        default: false
      },
      button: {
        default: true
      },
      variant: {
        type: String,
        default: 'normal'
      },
      type: {
        type: String,
        default: 'button'
      },
      'ok-button-text': {
        default: 'Yes, I am sure'
      },
      url: {
        type: String
      },
      method: {
        type: String,
        default: 'POST'
      },
      disabled: {
        // Only works for button mode at the moment.
        type: Boolean,
        default: false
      },
      send: {},
      success: {
        type: Function,
        default: function () {}
      }
    },
    methods: {
      performAction () {
        if (this.confirm) {
          this.$refs.confModal.show()
          return
        }
        this.submit()
      },
      successCallback (response) {
        if (this.confirm) {
          this.$refs.confModal.hide()
        }
        this.sending = false
        this.success(response)
      },
      failCallback (response) {
        this.sending = false
      },
      submit () {
        this.sending = true
        artCall(this.url, this.method, this.send, this.successCallback, this.failCallback)
      }
    },
    computed: {
      isDisabled () {
        return this.disabled || this.sending
      }
    }
  }
</script>

<style>
  .ac-action-container, .ac-action-div {
    display: inline-block;
  }
  .ac-action-div {
    cursor: pointer;
  }
</style>
