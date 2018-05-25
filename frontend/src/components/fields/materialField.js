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
          let sourceValidators = []
          if (Array.isArray(this.schema.validator)) {
            sourceValidators = this.schema.validator
          } else {
            sourceValidators.push(this.schema.validator)
          }
          let errors = []
          for (let validator of sourceValidators) {
            let err = validator(value, this.schema, this.model)
            if (err && err.length) {
              errors = errors.concat(err)
            }
          }
          if (errors.length) {
            return errors.join(', ')
          }
          return true
        })
      }
      return validators
    }
  },
  created () {
    EventBus.$on('form-failure', this.fetchErrors)
    EventBus.$on('reset-field-' + this.schema.model, this.clearErrors)
  },
  destroyed () {
    EventBus.$off('form-failure', this.fetchErrors)
    EventBus.$off('reset-field-' + this.schema.model, this.clearErrors)
  }
}
