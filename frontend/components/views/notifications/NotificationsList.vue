<template>
  <v-row no-gutters>
    <ac-paginated :show-pagination="false" :list="notifications">
      <template v-slot:default>
        <v-col cols="12">
          <v-list lines="three">
            <template v-for="(notification, index) in notifications.list">
              <template v-if="!notification.x!.event.recalled">
                <div
                    v-if="dynamicComponent(notification.x!.event.type)"
                    @click.left.capture="clickRead(notification)"
                    @click.middle.capture="clickRead(notification)"
                    :key="'container-' + index"
                >
                  <component :is="dynamicComponent(notification.x!.event.type)"
                             :key="notification.x!.id" v-observe-visibility="(value: boolean) => markRead(value, notification)"
                             class="notification" :notification="notification.x" :username="username"
                  />
                </div>
                <v-list-item v-else :key="index">
                  <v-row>
                    <v-col>
                      {{error(notification.x)}}
                      {{notification.x}}
                    </v-col>
                  </v-row>
                </v-list-item>
                <v-divider v-if="index + 1 < notifications.list.length" :key="`divider-${index}`"/>
              </template>
            </template>
          </v-list>
        </v-col>
      </template>
    </ac-paginated>
  </v-row>
</template>

<script setup lang="ts">
import {artCall, flatten} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {computed, defineComponent, onUnmounted, ref} from 'vue'
import {ObserveVisibility as vObserveVisibility} from 'vue-observe-visibility'
import AcRefund from './events/AcRefund.vue'
import AcDispute from './events/AcDispute.vue'
import AcFavorite from './events/AcFavorite.vue'
import AcSaleUpdate from './events/AcSaleUpdate.vue'
import AcOrderUpdate from './events/AcOrderUpdate.vue'
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
import AcWithdrawFailed from './events/AcWithdrawFailed.vue'
import AcLandscapeReferral from './events/AcLandscapeReferral.vue'
import AcSubmissionArtistTag from './events/AcSubmissionArtistTag.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcReferenceUploaded from '@/components/views/notifications/events/AcReferenceUploaded.vue'
import AcSubmissionShared from '@/components/views/notifications/events/AcSubmissionShared.vue'
import AcWaitlistUpdated from '@/components/views/notifications/events/AcWaitlistUpdated.vue'
import AcTipReceived from '@/components/views/notifications/events/AcTipReceived.vue'
import AcAutoClosed from '@/components/views/notifications/events/AcAutoClosed.vue'
import AcRevisionApproved from '@/components/views/notifications/events/AcRevisionApproved.vue'
import AcSubmissionKilled from '@/components/views/notifications/events/AcSubmissionKilled.vue'
import {useList} from '@/store/lists/hooks.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import type {AcNotification, NotificationStats, SubjectiveProps} from '@/types/main'

const components = {
  0: AcNewCharacter,
  3: AcCharTag,
  4: AcCommentNotification,
  6: AcNewProduct,
  7: AcCommissionsOpen,
  14: AcFavorite,
  15: AcDispute,
  16: AcRefund,
  17: AcSubmissionCharTag,
  18: AcOrderUpdate,
  19: AcSaleUpdate,
  21: AcSubmissionArtistTag,
  22: AcRevisionUploaded,
  23: AcSubmissionShared,
  24: AcCharShared,
  26: AcStreaming,
  27: AcRenewalFailure,
  28: AcSubscriptionDeactivated,
  29: AcRenewalFixed,
  30: AcNewJournal,
  32: AcWithdrawFailed,
  34: AcLandscapeReferral,
  35: AcReferenceUploaded,
  36: AcWaitlistUpdated,
  37: AcTipReceived,
  38: AcAutoClosed,
  39: AcRevisionApproved,
  40: AcSubmissionKilled,
}

declare interface NotificationsListProps extends SubjectiveProps {
  autoRead?: boolean,
  subset: string,
}

const props = withDefaults(defineProps<NotificationsListProps>(), {autoRead: true})
const {isCurrent} = useSubject({ props })

const error = (x: any) => {
  console.error(x)
}

const dynamicComponent = (type: number): ReturnType<typeof defineComponent> => {
  return components[type as keyof typeof components]
}

const readUrl = `/api/profiles/account/${props.username}/notifications/mark-read/`
const notifications = useList<AcNotification<any, any>>(props.subset + 'Notifications' + '__' + flatten(props.username))
const toMark = ref<Array<Partial<AcNotification<any, any>>>>([])
const marking = ref<Array<Partial<AcNotification<any, any>>>>([])
const marked = ref<Array<Partial<AcNotification<any, any>>>>([])

const stats = useSingle<NotificationStats>('notifications_stats__' + flatten(props.username))

const clickRead = (notification: SingleController<AcNotification<any, any>>) => {
  if (props.autoRead) {
    return
  }
  if (!isCurrent.value) {
    return
  }
  notification.updateX({read: true})
  artCall({
        url: `/api/profiles/account/${props.username}/notifications/mark-read/`,
        method: 'patch',
        data: [{
          id: (notification.x as AcNotification<any, any>).id,
          read: true,
        }],
      },
  ).then(stats.refresh)
}

const toMarkIDs = computed(() => toMark.value.map((x) => x.id))

const markedIDs = computed(() => marked.value.map((x) => x.id))


const markRead = (value: boolean, controller: SingleController<AcNotification<any, any>>) => {
  const notification = controller.x as AcNotification<any, any>
  if (!props.autoRead) {
    return
  }
  if (!value) {
    return
  }
  if (notification.read) {
    return
  }
  if (toMarkIDs.value.indexOf(notification.id) !== -1) {
    return
  }
  if (markedIDs.value.indexOf(notification.id) !== -1) {
    return
  }
  toMark.value.push({
    id: notification.id,
    read: true,
  })
}

const clearMarking = () => {
  // In case of failure, allow to try again.
  marking.value = []
}

const postMark = () => {
  for (const notification of marking.value) {
    const index = toMark.value.indexOf(notification)
    if (index > -1) {
      toMark.value.splice(index, 1)
      marked.value.push(notification)
    }
  }
  clearMarking()
  stats.refresh()
}

const readMonitor = () => {
  if (!isCurrent.value) {
    return
  }
  if (toMark.value.length && !marking.value.length) {
    marking.value = toMark.value
    artCall(
        {
          url: readUrl,
          method: 'patch',
          data: marking.value,
        },
    ).then(postMark).catch(clearMarking)
  }
}

const loopId = ref(window.setInterval(readMonitor, 3000))

onUnmounted(() => {
  readMonitor()
  window.clearInterval(loopId.value)
})
</script>
