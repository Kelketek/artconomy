import {EventBus} from '../../lib'

export default {
  data () {
    return {
      errors: []
    }
  },
  methods: {
    fetchErrors (errorSets) {
      for (let error of errorSets) {
        if (error.fieldName === this.schema.name) {
          this.errors.push(error.error)
        }
      }
    }
  },
  computed: {
    validators () {
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
  },
  destroyed () {
    EventBus.$off('form-failure', this.fetchErrors)
  }
}
