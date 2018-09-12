import AcPatchfield from '../components/ac-patchfield'
import AcAction from '../components/ac-action'

// Allows for editing of assets/characters/etc
export default {
  components: {
    AcPatchfield,
    AcAction
  },
  methods: {
    edit: function () {
      this.$router.history.replace({query: Object.assign({}, this.$route.query, { editing: true })})
    },
    lock: function () {
      let newQuery = {...this.$route.query}
      delete newQuery['editing']
      this.$router.history.replace({query: newQuery})
    },
    toggleEdit: function () {
      if (this.editing) {
        this.lock()
      } else {
        this.edit()
      }
    }
  },
  computed: {
    editing: {
      get () {
        return Boolean(this.controls && this.$route.query.editing)
      },
      set (value) {
        if (value) {
          this.edit()
        } else {
          this.lock()
        }
      }
    }
  }
}
