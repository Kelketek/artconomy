<template>
  <div>
    <v-layout wrap v-if="response !== null && !growing.length">
      <v-flex xs12 text-xs-center>
        <p>You do not have any notifications at this time.</p>
      </v-flex>
    </v-layout>
    <v-layout row v-else>
      <v-flex xs12 md10 offset-md1>
          <v-flex xs12 class="pl-2 mb-2">
            <h3>Your Notifications</h3>
          </v-flex>
      </v-flex>
    </v-layout>
    <v-layout row>
      <v-flex xs12 md10 offset-md1 v-if="growing">
        <v-list three-line>
          <template v-for="(notification, index) in growing">
            <component :is="dynamicComponent(notification.event.type)"
                       :key="notification.id" v-observe-visibility="markRead(notification.id)"
                       class="notification" :notification="notification"
                       v-if="dynamicComponent(notification.event.type)"
            />
            <v-list-tile v-else>
              <v-list-tile-content>
                {{$root.log(notification)}}
                {{notification}}
              </v-list-tile-content>
            </v-list-tile>
            <v-divider v-if="index + 1 < growing.length" :key="`divider-${index}`" />
          </template>
        </v-list>
      </v-flex>
    </v-layout>
    <v-layout row>
      <v-flex xs12 text-xs-center>
        <div v-if="(growing !== null) && furtherPagination" v-observe-visibility="moreNotifications"></div>
        <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcRefund from './notifications/ac-refund'
  import AcDispute from './notifications/ac-dispute'
  import AcFavorite from './notifications/ac-favorite'
  import AcSaleUpdate from './notifications/ac-sale-update'
  import AcOrderUpdate from './notifications/ac-order-update'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall, NOTIFICATION_MAPPING, EventBus } from '../lib'
  import AcSubmissionTag from './notifications/ac-submission-tag'
  import AcCharTag from './notifications/ac-char-tag'
  import AcSubmissionCharTag from './notifications/ac-submission-char-tag'
  import AcRevisionUploaded from './notifications/ac-revision-uploaded'
  import AcCommentNotification from './notifications/ac-comment-notification'
  import AcCharTransfer from './notifications/ac-char-transfer'
  import AcAssetShared from './notifications/ac-asset-shared'
  import AcCharShared from './notifications/ac-char-shared'
  import AcNewCharacter from './notifications/ac-new-character'
  import AcNewPortfolioItem from './notifications/ac-new-portfolio-item'
  import AcNewProduct from './notifications/ac-new-product'
  import AcNewPm from './notifications/ac-new-pm'
  import AcStreaming from './notifications/ac-streaming'
  import AcCommissionsOpen from './notifications/ac-commissions-open'

  export default {
    name: 'NotificationCenter',
    mixins: [Paginated],
    components: {
      AcCommissionsOpen,
      AcStreaming,
      AcNewPm,
      AcCharShared,
      AcAssetShared,
      AcCharTransfer,
      AcCommentNotification,
      AcRevisionUploaded,
      AcSubmissionCharTag,
      AcCharTag,
      AcSubmissionTag,
      AcRefund,
      AcDispute,
      AcFavorite,
      AcSaleUpdate,
      AcOrderUpdate,
      AcNewCharacter,
      AcNewPortfolioItem,
      AcNewProduct
    },
    directives: {'observe-visibility': ObserveVisibility},
    data () {
      return {
        url: '/api/profiles/v1/data/notifications/',
        toMark: [],
        marking: [],
        loopNotifications: false,
        growMode: true
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