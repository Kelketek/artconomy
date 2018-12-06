import $ from 'jquery'
import deepEqual from 'deep-equal'
import { artCall, buildQueryString, EventBus } from '../lib'
// For use with paginated Django views.
export default {
  props: {
    startingPage: { default: 1 },
    limit: { default: 24 },
    queryData: { default () { return {} } },
    counterName: { default: 'counter' },
    trackPages: { default: false },
    tabName: {},
    // Name of the tab currently in use, to compare against tabName.
    currentTab: {},
    // Whether we fetch once we've loaded immediately. Otherwise initial fetch will have to be handled by an outside
    // force.
    autoFetch: { default: true },
    showError: { default: false },
    tabShown: { default: true },
    emptyError: {
      default: 'We could not find anything which matched your request.'
    }
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
      promise: null,
      // Used with autoFetch to indicate when we've received the OK from the outside to manage ourselves.
      started: false,
      scrollToId: this.genId(),
      furtherPagination: true,
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
    genId () {
      let text = ''
      let possible = 'abcdefghijklmnopqrstuvwxyz'
      for (let i = 0; i < 20; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length))
      }
      return 'scroll-' + text
    },
    linkGen (pageNum) {
      let query = JSON.parse(JSON.stringify(this.queryData))
      query.page = pageNum
      return { path: this.baseURL, query: query }
    },
    restart () {
      this.growing = []
      this.currentPage = 1
      this.error = ''
      this.fetchItems()
    },
    performScroll () {
      this.$vuetify.goTo('#' + this.scrollToId, { offset: -100 })
    },
    loadMore () {
      if (this.currentPage >= this.totalPages) {
        return
      }
      if (this.fetching) {
        return
      }
      this.currentPage += 1
      this.fetchItems()
    },
    cease () {
      this.furtherPagination = false
      this.fetching = false
    },
    populateResponse (response) {
      this.promise = null
      this.error = ''
      this.response = response
      if (this.growMode) {
        if (this.growing === null) {
          this.growing = response.results
        } else {
          this.growing.push(...response.results)
        }
      } else {
        this.growing = response.results
      }
      this.fetching = false
      if (this.growing.length === 0 && ((this.queryData.q && this.queryData.q.length) || this.showError)) {
        this.error = this.emptyError
      }
      EventBus.$emit('result-count', { name: this.counterName, count: this.count })
    },
    populateError (response) {
      this.promise = null
      this.fetching = false
      if (response.status === 400) {
        if (response.responseJSON && response.responseJSON.error) {
          this.error = response.responseJSON.error
        } else {
          this.$error(response)
        }
      }
    },
    fetchItems () {
      this.started = true
      if (this.promise) {
        this.promise.abort()
        this.promise = null
      }
      let queryData = JSON.parse(JSON.stringify(this.queryData))
      queryData.page = this.currentPage
      queryData.size = this.pageSize
      let qs = buildQueryString(queryData)
      let url = `${this.url}?${qs}`
      this.fetching = true
      this.promise = artCall(url, 'GET', undefined, this.populateResponse, this.populateError)
    },
    setPageQuery (value) {
      let newQuery = { ...this.$route.query }
      newQuery['page'] = value
      let newRoute = { ...this.$route }
      newRoute.query = newQuery
      this.$router.history.replace(newRoute)
      if (newQuery.page) {
        this.currentPage = newQuery.page
      }
    },
    checkPageQuery (tabName) {
      if (this.tabName && this.tabName === tabName && this.trackPages) {
        this.setPageQuery(this.currentPage)
      }
    },
    bootstrap (tabName) {
      if (this.tabName && (tabName === this.tabName)) {
        this.$nextTick(() => {
          this.started = true
          this.fetchItems()
        })
      }
    }
  },
  computed: {
    canRun () {
      if (this.autoFetch) {
        return true
      }
      return this.started
    },
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
    currentPage (value) {
      if (!this.growMode && this.canRun) {
        this.fetchItems()
      }
      if (this.trackPages) {
        this.setPageQuery(value)
      }
    },
    queryData (newValue) {
      newValue = { ...newValue }
      if (!this.canRun) {
        this.oldQueryData = newValue
        return
      }
      if (!deepEqual(this.oldQueryData, newValue)) {
        this.restart()
        this.oldQueryData = newValue
      }
    }
  },
  updated () {
    let crawler = /bot|google|baidu|bing|msn|duckduckbot|teoma|slurp|yandex|Prerender/i
      .test(navigator.userAgent)
    crawler = crawler || this.$route.query._escaped_fragment_
    let self = this
    if (crawler) {
      $('.v-pagination__item').each((index, elem) => {
        let item = $(elem)
        let num = item.text()
        let newQuery = { ...self.$route.query }
        newQuery['page'] = num
        let newRoute = { ...self.$route }
        newRoute.query = newQuery
        let url = self.$router.resolve(newRoute).href
        item.wrap(`<a href="${url}"></a>`)
      })
    }
  },
  created () {
    EventBus.$on('tab-shown', this.checkPageQuery)
    EventBus.$on('bootstrap-tab', this.bootstrap)
    if (this.canRun) {
      this.fetchItems()
    }
  },
  destroyed () {
    EventBus.$off('tab-shown', this.checkPageQuery)
    EventBus.$off('bootstrap-tab', this.checkPageQuery)
  }
}
