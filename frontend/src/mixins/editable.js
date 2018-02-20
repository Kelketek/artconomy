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
      this.$router.history.replace({query: {}})
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
        return this.controls && this.$route.query.editing
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
