<template>
  <div class="form-container">
    <div v-if="errors.length" class="alert alert-danger">
      <a class="close" @click="dismiss_error">&times;</a>
      {% verbatim %}<span v-for="error in errors">{{ error }}</span>{% endverbatim %}
    </div>
    <div v-if="successes.length" class="alert alert-success">
      <a class="close" @click="dismiss_success">&times;</a>
      {% verbatim %}<span v-for="success in successes">{{ success }}</span>{% endverbatim %}
    </div>
    <div v-if="warnings.length" class="alert alert-warning">
      <a class="close" @click="dismiss_warning">&times;</a>
      {% verbatim %}<span v-for="warning in warnings">{{ warning }}</span>{% endverbatim %}
    </div>
    <vue-form-generator ref="form" :schema="schema" :model="model"
                        :options="options"></vue-form-generator>
    <fieldset>
      <slot></slot>
    </fieldset>
  </div>
</template>

<script>
  import $ from 'jquery'
  import {setErrors} from '../lib'

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
          }
        }
        // Make sure we don't screw up our 'saved' setting.
        this.oldValue = defaults
      },
      // To fix this properly I would need to make an update upstream. If it becomes enough of an issue, I might.
      // For now, jQuery will do.
      disable: function () {
        $(this.$el).find('fieldset').attr('disabled', true)
      },
      enable: function () {
        $(this.$el).find('fieldset').attr('disabled', false)
      },
      submit: function () {
        this.disable()
        this.errors = []
        this.successes = []
        this.warnings = []
        let self = this
        this.$refs.form.validate()
        if (this.$refs.form.errors.length) {
          this.enable()
          return
        }
        $.ajax({
          url: self.url,
          method: self.method,
          data: JSON.stringify(self.model),
          processData: true,
          contentType: 'application/json; charset=utf-8',
          dataType: 'json',
          success: self.success_hook,
          error: self.failure_hook
        })
      },
      success_hook: function (response, event) {
        this.success(response)
        if (this.resetAfter) {
          this.reset()
        }
        this.saved = true
        this.enable()
      },
      failure_hook: function (response, event) {
        setErrors(this.$refs.form, response.responseJSON)
        this.enable()
      }
    },
    created: function () {
      let defaults = {}
      for (let key in this.model) {
        if (this.model.hasOwnProperty(key)) {
          defaults[key] = this.model[key]
        }
      }
      function genDefaults () {
        return {...defaults}
      }
      this.defaults = genDefaults
    },
    data: function () {
      return {
        successes: [],
        errors: [],
        warnings: [],
        saved: false,
        defaults: function () {
          return {}
        },
        oldValue: {}
      }
    },
    watch: {
      model: {
        handler (newValue) {
          // Vue has a limitation where objects may be marked as changed when they have not always been
          let changed = false
          for (let key of Object.keys(newValue)) {
            if (newValue[key] !== this.oldValue[key]) {
              changed = true
              this.saved = false
              break
            }
          }
          // Make a copy of the old object. Don't do this unless we've detected a change or it can cause the watcher
          // to think another change has been made in a weird way. Not sure why.
          if (changed) {
            this.oldValue = JSON.parse(JSON.stringify(newValue))
          }
        },
        deep: true,
        immediate: true
      }
    }
  }
</script>
