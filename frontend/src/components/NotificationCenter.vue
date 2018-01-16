<template>
  <div class="notifications-center container">
    <div v-if="response !== null && !growing.length" class="row">
      <div class=" col-sm-12 text-center">
        <p>You do not have any notifications at this time.</p>
      </div>
    </div>
    <div v-else>
      <div class="row mt-3">
        <h3>Your Notifications</h3>
      </div>
      <div
          v-for="notification in growing"
          :key="notification.id"
          v-observe-visibility="markRead(notification.id)"
          class="notification" :class="{'unread': !notification.read}">
        <component :is="dynamicComponent(notification.event.type)" :event="notification.event" />
      </div>
    </div>
    <div class="row">
      <div class="col-sm-12 text-center">
        <div v-if="growing !== null" v-observe-visibility="moreNotifications"></div>
        <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  @import '../custom-bootstrap';
  .notification {
    border-bottom: 1px solid $dark-gray;
  }
  .unread {
    background-color: #ffefff;
  }
</style>

<script>
  import Paginated from '../mixins/paginated'
  import AcRefund from './notifications/ac-refund'
  import AcDispute from './notifications/ac-dispute'
  import AcFavorite from './notifications/ac-favorite'
  import AcSaleUpdate from './notifications/ac-sale-update'
  import AcOrderUpdate from './notifications/ac-order-update'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall, NOTIFICATION_MAPPING, EventBus } from '../lib'

  export default {
    name: 'NotificationCenter',
    mixins: [Paginated],
    components: {AcRefund, AcDispute, AcFavorite, AcSaleUpdate, AcOrderUpdate},
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
      dynamicComponent (type) {
        return NOTIFICATION_MAPPING[type + '']
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
        EventBus.$emit('notifications-updated')
      },
      readMonitor () {
        if (this.loopNotifications && this.toMark.length && !this.marking.length) {
          this.marking = this.toMark
          artCall(`${this.url}mark-read/`, 'PATCH', this.marking, this.postMark, this.clearMarking)
        }
        if (this.loopNotifications) {
          this.$setTimer('markNotificationsRead', this.readMonitor, 3000)
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