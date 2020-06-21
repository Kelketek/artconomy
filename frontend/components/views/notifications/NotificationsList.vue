<template>
  <v-row no-gutters >
    <ac-paginated :show-pagination="false" :list="notifications">
      <template v-slot:default>
        <v-col cols="12" md="10" offset-md="1">
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
              <v-list-item v-else :key="index">
                <v-list-item-content>
                  {{error(notification.x)}}
                  {{notification.x}}
                </v-list-item-content>
              </v-list-item>
              <v-divider v-if="index + 1 < notifications.list.length" :key="`divider-${index}`"/>
            </template>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-row>
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
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import Component, {mixins} from 'vue-class-component'
import AcReferenceUploaded from '@/components/views/notifications/events/AcReferenceUploaded.vue'
import AcSubmissionShared from '@/components/views/notifications/events/AcSubmissionShared.vue'

@Component({components: {
  AcSubmissionShared,
  AcReferenceUploaded,
  AcPaginated,
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
}})
export default class NotificationsList extends mixins(NotificationsListBase) {
  error(x: any) {
    console.error(x)
  }
}
</script>
