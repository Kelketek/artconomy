import {EventBus} from '../../lib'

export default {
  data () {
    return {
      errors: [],
      cleared: false
    }
  },
  methods: {
    fetchErrors (errorSets) {
      for (let error of errorSets) {
        if (error.field.model === this.schema.model) {
          this.errors.push(error.error)
        }
      }
    },
    clearErrors () {
      this.errors = []
      this.cleared = true
    }
  },
  computed: {
    validators () {
      // This is a hack to make sure that the validators aren't triggered when the form is reset.
      if (this.cleared) {
        return []
      } else {
        this.cleared = false
        return this.validatorSet
      }
    },
    validatorSet () {
      let validators = []
      if (this.schema.validator) {
        validators.push((value) => {
          let err = this.schema.validator(value, this.schema, this.value)
          if (err && err.length) {
            return err.join(', ')
          }
          return true
        })
      }
      return validators
    }
  },
  created () {
    EventBus.$on('form-failure', this.fetchErrors)
    console.log('Listening on ' + 'reset-field-' + this.schema.model)
    EventBus.$on('reset-field-' + this.schema.model, this.clearErrors)
  },
  destroyed () {
    EventBus.$off('form-failure', this.fetchErrors)
    EventBus.$off('reset-field-' + this.schema.model, this.clearErrors)
  }
}
