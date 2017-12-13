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
      }
    },
    methods: {
      reset: function () {
        let defaults = this.defaults()
        for (let key in defaults) {
          if (defaults.hasOwnProperty(key)) {
            this.model[key] = defaults[key]
          }
        }
      },
      // To fix this properly I would need to make an update upstream. If it becomes enough of an issue, I might.
      // For now, jQuery will do.
      disable: function () {
        $(this.$el).find('fieldset').attr('disabled', true)
      },
      enable: function () {
        $(this.$el).find('fieldset').attr('disabled', false)
      },
      // serialize: function () {
      //   return new FormData(this.getForm())
      // },
      // getForm: function () {
      //   let $el = $(this.$el);
      //   if (!(this.$el.tagName === 'FORM')) {
      //     let candidate = $el.parents('form')
      //     if (candidate.length === 0) {
      //       $el = $el.find('form')
      //     } else {
      //       $el = candidate
      //     }
      //   }
      //   let $cloned = $el.clone();
      //   // get original selects into a jq object
      //   let $originalSelects = $el.find('select')
      //   $cloned.find('select').each(function (index, item) {
      //     // set new select to value of old select
      //     $(item).val($originalSelects.eq(index).val())
      //   })
      //   $el = $cloned
      //
      //   // Normal file fields. May no longer be needed.
      //   $el.find('input[type=file]').each(function () {
      //     let field = $(this)
      //     if (!field.val()) {
      //       field.remove()
      //     }
      //   })
      //   return $el[0]
      // },
      submit: function () {
        this.disable()
        this.errors = []
        this.successes = []
        this.warnings = []
        let self = this
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
        this.reset()
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
        defaults: function () {
          return {}
        }
      }
    }
  }
</script>
