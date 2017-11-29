<template>
  <div class="ac-action-container">
    <b-button v-if="button" :variant="variant" :type="type" @click="performAction"><slot></slot></b-button>
    <div class="ac-action-div" @click="performAction"><slot @click="performAction"></slot></div>
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
      callback (response) {
        if (this.confirm) {
          this.$refs.confModal.hide()
        }
        this.success(response)
      },
      submit () {
        artCall(this.url, this.method, this.send, this.callback)
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
