<template>
  <v-dialog
      v-model="toggle"
      fullscreen
      ref="dialog"
      transition="dialog-bottom-transition"
      :overlay="false"
      scrollable
  >
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="toggle = false" dark>
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>{{title}}</v-toolbar-title>
        <v-spacer />
        <v-toolbar-items>
          <v-btn dark flat @click.prevent="$refs.form.submit">{{ submitText }}</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-form @submit.prevent="$refs.form.submit">
          <slot name="header" />
          <ac-form-container
              ref="form" v-bind="$attrs"
              :schema="schema" :model="model"
              :options="options" :method="method"
              :success="success" :failure="failure"
              :url="url" :pre-send="preSend"
              :reset-after="resetAfter"
          />
          <slot name="footer" />
          <v-btn type="submit" class="hidden" />
          <v-layout row wrap class="hidden-xs-only">
            <v-flex xs12 text-xs-center mt-4>
              <v-btn color="primary" @click.prevent="$refs.form.submit">{{ submitText }}</v-btn>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style scoped>
  .hidden {
    display: none;
  }
</style>

<script>
  import AcFormContainer from './ac-form-container'
  import { EventBus } from '../lib'
  import Vue from 'vue'

  export default {
    components: {AcFormContainer},
    props: {
      submitText: {
        default: 'Submit'
      },
      title: {
        default: ''
      },
      value: {},
      url: {
      },
      method: {
        type: String,
        default: 'POST'
      },
      success: {
        type: Function,
        default: function (response) {}
      },
      failure: {
        type: Function,
        default: function (response) {}
      },
      schema: {
        type: Object,
        default: function () {
          return {}
        }
      },
      model: {
        type: Object,
        default: function () {
          return {}
        }
      },
      options: {
        type: Object,
        default: function () {
          return {}
        }
      },
      preSend: {
        // For modifying the data before it goes out.
        type: Function,
        default: function (data) {
          return data
        }
      },
      resetAfter: {
        type: Boolean,
        default: function () {
          return true
        }
      }
    },
    computed: {
      toggle: {
        get () {
          return this.value
        },
        set (value) {
          this.$emit('input', value)
        }
      }
    },
    methods: {
      scrollToErrors (event) {
        Vue.nextTick(() => {
          if (document.querySelector('.error--text')) {
            this.$refs.dialog.$vuetify.goTo('.error--text')
          }
        })
      }
    },
    created () {
      EventBus.$on('form-error', this.scrollToErrors)
      EventBus.$on('form-failure', this.scrollToErrors)
    },
    destroyed () {
      EventBus.$off('form-error', this.scrollToErrors)
      EventBus.$off('form-failure', this.scrollToErrors)
    }
  }
</script>