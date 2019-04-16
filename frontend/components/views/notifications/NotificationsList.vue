<template>
  <v-layout wrap>
    <v-flex xs12 text-xs-center v-if="notifications.ready !== null && !notifications.list.length">
      <p>You do not have any notifications at this time.</p>
    </v-flex>
    <v-flex xs12 md10 offset-md1 v-if="notifications.list.length">
      <v-list three-line>
        <template v-for="(notification, index) in notifications.list">
          <div
              v-if="dynamicComponent(notification.x.event.type)"
              @click.left.capture="clickRead(notification)"
              @click.middle.capture="clickRead(notification)"
              :key="'container-' + index"
          >
            <component :is="dynamicComponent(notification.x.event.type)"
                       :key="notification.x.id" v-observe-visibility="markRead(notification)"
                       class="notification" :notification="notification.x"
            />
          </div>
          <v-list-tile v-else :key="index">
            <v-list-tile-content>
              {{log(notification.x)}}
              {{notification.x}}
            </v-list-tile-content>
          </v-list-tile>
          <v-divider v-if="index + 1 < notifications.list.length" :key="`divider-${index}`"/>
        </template>
      </v-list>
    </v-flex>
    <v-flex xs12 text-xs-center>
      <ac-grow-spinner :list="notifications"></ac-grow-spinner>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import AcRefund from './events/AcRefund.vue'
import AcDispute from './events/AcDispute.vue'
import AcFavorite from './events/AcFavorite.vue'
import AcSaleUpdate from './events/AcSaleUpdate.vue'
import AcOrderUpdate from './events/AcOrderUpdate.vue'
import AcSubmissionTag from './events/AcSubmissionTag.vue'
import AcCharTag from './events/AcCharTag.vue'
import AcSubmissionCharTag from './events/AcSubmissionCharTag.vue'
import AcRevisionUploaded from './events/AcRevisionUploaded.vue'
import AcCommentNotification from './events/AcCommentNotification.vue'
import AcAssetShared from './events/AcAssetShared.vue'
import AcCharShared from './events/AcCharShared.vue'
import AcNewCharacter from './events/AcNewCharacter.vue'
import AcNewProduct from './events/AcNewProduct.vue'
import AcStreaming from './events/AcStreaming.vue'
import AcCommissionsOpen from './events/AcCommissionsOpen.vue'
import AcRenewalFixed from './events/AcRenewalFixed.vue'
import AcRenewalFailure from './events/AcRenewalFailure.vue'
import AcSubscriptionDeactivated from './events/AcSubscriptionDeactivated.vue'
import AcNewJournal from './events/AcNewJournal.vue'
import NotificationsListBase from './mixins/notifications-list-base'
import AcOrderTokenIssued from './events/AcOrderTokenIssued.vue'
import AcWithdrawFailed from './events/AcWithdrawFailed.vue'
import AcPortraitReferral from './events/AcPortraitReferral.vue'
import AcLandscapeReferral from './events/AcLandscapeReferral.vue'
import AcSubmissionArtistTag from './events/AcSubmissionArtistTag.vue'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'

export default {
  name: 'ac-list-notifications',
  mixins: [NotificationsListBase],
  components: {
    AcGrowSpinner,
    AcSubmissionArtistTag,
    AcLandscapeReferral,
    AcPortraitReferral,
    AcWithdrawFailed,
    AcOrderTokenIssued,
    AcNewJournal,
    AcSubscriptionDeactivated,
    AcRenewalFailure,
    AcRenewalFixed,
    AcCommissionsOpen,
    AcStreaming,
    AcCharShared,
    AcAssetShared,
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
    AcNewProduct,
  },
  props: {
    autoFetch: {default: false},
  },
  methods: {
    log(x: any) {
      console.log(x)
    },
  },
}
</script>
