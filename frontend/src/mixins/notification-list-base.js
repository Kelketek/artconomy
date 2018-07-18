import {artCall, NOTIFICATION_MAPPING, EventBus} from '../lib'

export default {
  props: ['subset', 'hostTab', 'autoRead'],
  data () {
    return {
      baseUrl: '/api/profiles/v1/data/notifications/',
      url: `/api/profiles/v1/data/notifications/${this.subset}/`,
      toMark: [],
      marking: [],
      // It's unlikely to be an issue in reality, but this does technically go on forever.
      // in theory someone could scroll far enough to bring their machine to its knees.
      marked: [],
      loopNotifications: this.hostTab === this.subset,
      growMode: true
    }
  },
  methods: {
    moreNotifications (isVisible) {
      if (isVisible) {
        this.currentPage += 1
      }
    },
    dynamicComponent (type) {
      return NOTIFICATION_MAPPING[type + '']
    },
    populateNotifications (response) {
      this.response = response
      this.growing = response.results
      this.fetching = false
    },
    clickRead (notification) {
      if (this.autoRead) {
        return
      }
      notification.read = true
      artCall(`${this.baseUrl}mark-read/`, 'PATCH', [{id: notification.id, read: true}], this.sendUpdateEvent)
    },
    markRead (notification) {
      if (!this.autoRead) {
        return () => {}
      }
      return () => {
        let self = this
        if (notification.read) {
          return
        }
        if (this.toMarkIDs.indexOf(notification.id) !== -1) {
          return
        }
        if (this.markedIDs.indexOf(notification.id) !== -1) {
          return
        }
        self.toMark.push({id: notification.id, read: true})
      }
    },
    clearMarking () {
      // In case of failure, allow to try again.
      this.marking = []
    },
    sendUpdateEvent () {
      EventBus.$emit('notifications-updated')
    },
    postMark () {
      for (let notification of this.marking) {
        let index = this.toMark.indexOf(notification)
        if (index > -1) {
          this.toMark.splice(index, 1)
          this.marked.push(notification)
        }
      }
      this.clearMarking()
      EventBus.$emit('notifications-updated')
    },
    readMonitor () {
      if (this.loopNotifications && this.toMark.length && !this.marking.length) {
        this.marking = this.toMark
        artCall(`${this.baseUrl}mark-read/`, 'PATCH', this.marking, this.postMark, this.clearMarking)
      }
      if (this.loopNotifications) {
        this.$setTimer('markNotificationsRead-' + this.subset, this.readMonitor, 3000)
      }
    },
    startMonitoring () {
      this.loopNotifications = true
      this.readMonitor()
    },
    stopMonitoring () {
      this.loopNotifications = false
      this.$clearTimer('markNotificationsRead-' + this.subset)
    }
  },
  watch: {
    hostTab (value) {
      if ((this.subset === value && this.autoRead)) {
        this.startMonitoring()
      } else {
        this.stopMonitoring()
      }
    }
  },
  computed: {
    toMarkIDs () {
      return this.toMark.map(x => x.id)
    },
    markedIDs () {
      return this.marked.map(x => x.id)
    }
  },
  created () {
    this.fetchItems()
    if (this.loopNotifications && this.autoRead) {
      this.startMonitoring()
    }
  }
}
