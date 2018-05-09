<template>
  <div class="form-container">
    <div class="loading-overlay" v-if="sending">
        <div class="spinner-holder"><i class="fa fa-spinner fa-5x fa-spin"></i></div>
    </div>
    <vue-form-generator ref="form" :schema="schema" :model="model"
                        :options="options" />
    <v-alert value="error" v-for="error in errors" v-if="errors.length" type="error" :key="error">
      {{error}}<div class="error-right"><a class="close" @click="dismissError"><v-icon>close</v-icon></a></div>
    </v-alert>
    <fieldset>
      <slot />
    </fieldset>
  </div>
</template>

<style scoped>
  .loading-overlay {
    position: absolute;
    top: 0;
    right: 0;
    height: 100%;
    width: 100%;
    z-index: 1;
    background-color: black;
    vertical-align: center;
    opacity: .5;
    box-shadow: 0 0 0 .20em black;
  }
  .form-container {
    position: relative;
  }
  .spinner-holder {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    text-align: center;
    height: 30%;
    margin: auto;
  }
  .error-right {
    float: right;
    display: inline-block
  }
</style>

<script>
  import $ from 'jquery'
  import deepEqual from 'deep-equal'
  import { setErrors, EventBus } from '../lib'

  export default {
    name: 'ac-form-container',
    props: {
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
      },
      value: {}
    },
    methods: {
      reset: function () {
        let defaults = this.defaults()
        for (let key in defaults) {
          if (defaults.hasOwnProperty(key)) {
            this.model[key] = defaults[key]
            EventBus.$emit('reset-field-' + key, defaults[key])
          }
        }
        // Make sure we don't screw up our 'saved' setting.
        this.oldValue = defaults
      },
      dismissError () {
        this.errors = []
      },
      // To fix this properly I would need to make an update upstream. If it becomes enough of an issue, I might.
      // For now, jQuery will do.
      disable () {
        $(this.$el).find('fieldset').attr('disabled', true)
        this.sending = true
      },
      enable () {
        $(this.$el).find('fieldset').attr('disabled', false)
        this.sending = false
      },
      submit () {
        if (this.disabled) {
          return
        }
        this.disable()
        this.errors = []
        this.successes = []
        this.warnings = []
        let self = this
        this.$refs.form.validate()
        if (this.$refs.form.errors.length) {
          this.enable()
          EventBus.$emit('form-error', this)
          return
        }
        let form = new FormData()
        let data = this.getData()
        for (let [field, value] of Object.entries(data)) {
          if (Array.isArray(value)) {
            for (let item of value) {
              form.append(field, item)
            }
          } else {
            form.append(field, value)
          }
        }
        $.ajax({
          url: self.url,
          method: self.method,
          data: form,
          cache: false,
          contentType: false,
          processData: false,
          success: self.success_hook,
          error: self.failure_hook
        })
      },
      success_hook (response, event) {
        if (this.resetAfter) {
          this.reset()
        }
        this.saved = true
        this.success(response)
        this.enable()
      },
      getData () {
        let data = {...this.model}
        for (let field of this.schema.fields) {
          if (field.type === 'v-file-upload') {
            let result = []
            for (let file of data[field.model]) {
              result.push(file.file)
            }
            data[field.model] = result
          }
        }
        return data
      },
      failure_hook (response, event) {
        setErrors(this.$refs.form, response.responseJSON, this.errors)
        this.enable()
      }
    },
    created () {
      let defaults = JSON.parse(JSON.stringify(this.model))
      function genDefaults () {
        return {...defaults}
      }
      this.defaults = genDefaults
    },
    data () {
      return {
        successes: [],
        errors: [],
        warnings: [],
        saved: false,
        defaults: function () {
          return {}
        },
        oldValue: {},
        sending: false
      }
    },
    watch: {
      model: {
        handler (newValue) {
          let changed = !deepEqual(this.oldValue, newValue)
          // Make a copy of the old object. Don't do this unless we've detected a change or it can cause the watcher
          // to think another change has been made in a weird way. Not sure why.
          if (changed) {
            this.saved = false
            this.oldValue = JSON.parse(JSON.stringify(newValue))
          }
        },
        deep: true,
        immediate: true
      }
    }
  }
</script>
