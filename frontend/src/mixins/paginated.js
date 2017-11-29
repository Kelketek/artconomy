import {artCall} from '../lib'
// For use with paginated Django views.
export default {
  props: {
    startingPage: {default: 1},
    limit: 10
  },
  data: function () {
    return {
      currentPage: parseInt(this.$route.query.page || 1),
      baseURL: this.$route.path,
      response: null,
      growing: null,
      fetching: false
    }
  },
  methods: {
    linkGen (pageNum) {
      return {path: this.baseURL, query: {page: pageNum}}
    },
    growList (response) {
      console.log('Growing.')
      this.response = response
      this.growing.push.apply(this.growing, this.response.results)
      this.fetching = false
    },
    loadMore () {
      if (this.currentPage >= this.totalPages) {
        return
      }
      this.fetching = true
      this.currentPage += 1
      artCall(this.$router.resolve(this.linkGen(this.currentPage)).route.fullPath, 'GET', undefined, this.growList)
    }
  },
  computed: {
    totalPages: function () {
      return Math.ceil(this.response.count / this.response.size)
    },
    pageSize: function () {
      return this.response.size
    }
  }
}
