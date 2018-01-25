import deepEqual from 'deep-equal'
import { artCall, buildQueryString, EventBus } from '../lib'
// For use with paginated Django views.
export default {
  props: {
    startingPage: {default: 1},
    limit: {default: 10},
    // Set false to use the never ending mode via the growing list.
    pageReload: {default: true},
    queryData: {default () { return {} }},
    counterName: {default: 'counter'}
  },
  data: function () {
    let defaults = {
      currentPage: parseInt(this.$route.query.page || 1),
      // Display page path.
      baseURL: this.$route.path,
      response: null,
      growing: null,
      growMode: false,
      fetching: false,
      error: '',
      oldQueryData: JSON.parse(JSON.stringify(this.queryData))
    }
    if (this.url === undefined) {
      // The URL of the API endpoint. Sometimes this is a prop, so conditionally provide it.
      defaults.url = 'api/v1/paginated/'
    }
    return defaults
  },
  methods: {
    linkGen (pageNum) {
      let query = JSON.parse(JSON.stringify(this.queryData))
      query.page = pageNum
      return {path: this.baseURL, query: query}
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
      this.error = ''
      this.response = response
      if (this.growMode) {
        this.growing.push(response.results)
      } else {
        this.growing = response.results
      }
      this.fetching = false
      if (this.growing.length === 0 && this.queryData.q && this.queryData.q.length) {
        this.error = 'We could not find anything which matched your request.'
      }
      EventBus.$emit('result-count', {name: this.counterName, count: this.count})
    },
    populateError (response) {
      if (response.status === 400) {
        if (response.responseJSON && response.responseJSON.error) {
          this.error = response.responseJSON.error
        } else {
          this.$error(response)
        }
      }
    },
    fetchItems (pageNum) {
      let queryData = JSON.parse(JSON.stringify(this.queryData))
      queryData.page = this.currentPage
      queryData.size = this.pageSize
      let qs = buildQueryString(queryData)
      let url = `${this.url}?${qs}`
      this.fetching = true
      artCall(url, 'GET', undefined, this.populateResponse, this.populateError)
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
    },
    count () {
      return this.response && this.response.count
    }
  },
  watch: {
    currentPage () {
      if (this.pageReload) {
        this.fetchItems()
      }
    },
    queryData (newValue) {
      if (!deepEqual(this.oldQueryData, newValue)) {
        this.currentPage = 1
        this.error = ''
        this.fetchItems()
        this.oldQueryData = JSON.parse(JSON.stringify(newValue))
      }
    }
  }
}
