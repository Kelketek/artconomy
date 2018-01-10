import {artCall} from '../lib'
// For use with paginated Django views.
export default {
  props: {
    startingPage: {default: 1},
    limit: {default: 10},
    // Set false to use the never ending mode via the growing list.
    pageReload: {default: true}
  },
  data: function () {
    let defaults = {
      currentPage: parseInt(this.$route.query.page || 1),
      // Display page path.
      baseURL: this.$route.path,
      response: null,
      growing: null,
      growMode: false,
      fetching: false
    }
    if (this.url === undefined) {
      // The URL of the API endpoint. Sometimes this is a prop, so conditionally provide it.
      defaults.url = 'api/v1/paginated/'
    }
    return defaults
  },
  methods: {
    linkGen (pageNum) {
      return {path: this.baseURL, query: {page: pageNum}}
    },
    loadMore () {
      if (this.currentPage >= this.totalPages) {
        return
      }
      this.fetching = true
      this.currentPage += 1
      artCall(this.$router.resolve(this.linkGen(this.currentPage)).route.fullPath, 'GET', undefined, this.growList)
    },
    populateResponse (response) {
      this.response = response
      if (this.growMode) {
        this.growing.push(response.results)
      } else {
        this.growing = response.results
      }
      this.fetching = false
    },
    fetchItems (pageNum) {
      let url = `${this.url}?page=${this.currentPage}&size=${this.pageSize}`
      this.fetching = true
      artCall(url, 'GET', undefined, this.populateResponse)
    }
  },
  computed: {
    totalPages: function () {
      if (!this.response) {
        return 0
      }
      return Math.ceil(this.response.count / this.response.size)
    },
    pageSize: function () {
      if (this.response) {
        return this.response.size
      }
      return this.limit
    },
    nonEmpty: function () {
      if (!this.response) {
        return false
      } else if (this.response.results.length === 0) {
        return false
      }
      return true
    }
  },
  watch: {
    currentPage () {
      if (this.pageReload) {
        this.fetchItems()
      }
    }
  }
}
