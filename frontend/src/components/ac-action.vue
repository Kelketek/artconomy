<template>
  <div class="ac-action-container">
    <v-btn
        v-if="button"
        :disabled="isDisabled"
        :type="type"
        @click.native.stop="performAction"
        :dark="dark"
        :fixed="fixed"
        :color="color || variant"
        :bottom="bottom"
        :small="small"
        :top="top"
        :left="left"
        :right="right"
        :fab="fab"
    >
      <slot />
    </v-btn>
    <div v-else @click="performAction" class="clickable"><slot /></div>
    <v-dialog v-model="showModal" max-width="500px" v-if="confirm">
      <v-card>
        <v-card-title>
          <slot name="confirmation-text">
            Are you sure?
          </slot>
          <v-spacer />
        </v-card-title>
        <v-card-actions right>
          <v-btn flat @click.stop="showModal=false">Cancel</v-btn>
          <v-btn flat color="red" @click.stop="submit">Yes, I am sure.</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <div v-if="error" class="ac-action-error">
      <p><strong>ERROR: </strong>{{error}}</p>
    </div>
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
      dark: {},
      fixed: {},
      color: {},
      bottom: {},
      right: {},
      left: {},
      fab: {},
      top: {},
      small: {},
      success: {
        type: Function,
        default: function () {}
      }
    },
    data () {
      return {
        sending: false,
        error: '',
        showModal: false
      }
    },
    methods: {
      performAction () {
        if (this.confirm) {
          this.showModal = true
          return
        }
        this.submit()
      },
      successCallback (response) {
        if (this.confirm) {
          this.showModal = false
        }
        this.sending = false
        this.success(response)
      },
      failCallback (response) {
        this.sending = false
        if (response.responseJSON && response.responseJSON['error']) {
          this.error = response.responseJSON['error']
        }
      },
      submit () {
        this.sending = true
        this.error = ''
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
