<template>
  <v-dialog
      v-model="toggle"
      fullscreen
      transition="dialog-bottom-transition"
      :overlay="false"
      scrollable
  >
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="toggle = false" dark>
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>New Product</v-toolbar-title>
        <v-spacer />
        <v-toolbar-items>
          <v-btn dark flat @click.prevent="$refs.form.submit">Create</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-form @submit.prevent="$refs.form.submit">
          <ac-form-container
              ref="form" v-bind="$attrs"
              :schema="schema" :model="model"
              :options="options" :method="method"
              :success="success" :failure="failure"
              :url="url" :pre-send="preSend"
              :reset-after="resetAfter"
          />
          <v-btn type="submit" class="hidden" />
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
    }
  }
</script>