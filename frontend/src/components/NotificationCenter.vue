<template>
  <div class="notifications-center container">
    <div class="row">
      <div v-if="response !== null && !growing.length" class="col-sm-12 text-center">
        <p>You do not have any notifications at this time.</p>
      </div>
      <div v-else>
        <div
            v-for="notification in growing"
            :key="notification.id"
            :notification="notification"
            v-observe-visibility="markRead(notification.id)"
            class="col-sm-12">
          {{notification}}
        </div>
      </div>
      <div class="col-sm-12 text-center">
        <div v-if="growing !== null" v-observe-visibility="moreNotifications"></div>
        <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      </div>
    </div>
  </div>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall } from '../lib'

  export default {
    name: 'NotificationCenter',
    mixins: [Paginated],
    directives: {'observe-visibility': ObserveVisibility},
    data () {
      return {
        url: '/api/profiles/v1/data/notifications/',
        toMark: [],
        marking: [],
        loopNotifications: false
      }
    },
    methods: {
      moreNotifications (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      },
      populateNotifications (response) {
        this.response = response
        this.growing = response.results
        this.fetching = false
      },
      markRead (id) {
        let self = this
        return () => {
          self.toMark.push({id: id, read: true})
        }
      },
      clearMarking () {
        // In case of failure, allow to try again.
        this.marking = []
      },
      postMark () {
        for (let notification of this.marking) {
          let index = this.toMark.indexOf(notification)
          if (index > -1) {
            this.toMark.splice(index, 1)
          }
        }
      },
      readMonitor () {
        if (this.loopNotifications && this.toMark.length && !this.marking.length) {
          this.marking = this.toMark
          artCall(`${this.url}mark-read/`, 'PATCH', this.marking, this.postMark, this.clearMarking)
        }
        if (this.loopNotifications) {
          this.$setTimer('markNotificationsRead', this.readMonitor, 5000)
        }
      },
      startMonitoring () {
        if (this.viewer && this.viewer.username) {
          if (!this.loopNotifications) {
            this.loopNotifications = true
            this.readMonitor()
          }
        } else {
          this.loopNotifications = false
        }
      }
    },
    created () {
      this.fetchItems()
      this.startMonitoring()
    },
    watch: {
      viewer () {
        this.startMonitoring()
      }
    }
  }
</script>