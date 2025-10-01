<template>
  <v-navigation-drawer
    v-model="drawer"
    location="right"
    temporary
    :width="width"
    class="message-center"
  >
    <template #prepend>
      <v-toolbar prominent>
        <v-btn icon variant="plain" @click="drawer = false">
          <v-icon :icon="mdiChevronRight" />
        </v-btn>
        <v-tabs v-model="section" fixed-tabs>
          <v-tab :value="0">
            Community<span v-if="counts.community_count"
              >&nbsp;({{ counts.community_count }})</span
            >
          </v-tab>
          <v-tab :value="1">
            Sales/Orders<span v-if="counts.sales_count"
              >&nbsp;({{ counts.sales_count }})</span
            >
          </v-tab>
        </v-tabs>
        <v-spacer />
        <v-btn
          variant="flat"
          icon
          color="primary"
          aria-label="Mark all as read"
          @click="markAllRead"
        >
          <v-icon :icon="mdiRead" />
        </v-btn>
      </v-toolbar>
    </template>
    <v-window v-model="section">
      <v-window-item :value="0">
        <notifications-list
          subset="community"
          :username="username"
          :auto-read="isCurrent"
        />
      </v-window-item>
      <v-window-item :value="1">
        <notifications-list
          subset="sales"
          :username="username"
          :auto-read="false"
        />
      </v-window-item>
    </v-window>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useSubject } from "@/mixins/subjective.ts"
import { useSingle } from "@/store/singles/hooks.ts"
import { computed, ref, watch } from "vue"
import { useDisplay } from "vuetify"
import { mdiChevronRight, mdiRead } from "@mdi/js"
import NotificationsList from "@/components/views/notifications/NotificationsList.vue"
import { useList } from "@/store/lists/hooks.ts"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { artCall, flatten } from "@/lib/lib.ts"
import type {
  AcNotification,
  NotificationStats,
  SubjectiveProps,
} from "@/types/main"

const drawer = defineModel<boolean>({ required: true })
const display = useDisplay()
const props = defineProps<SubjectiveProps>()
const { subject, isCurrent } = useSubject({ props })
const section = ref(0)
const width = computed(() => {
  if (!drawer.value) {
    // Bug in upstream causes any value to be used for forcing the tray open on mobile.
    return undefined
  }
  if (display.width.value < 800) {
    return "100%"
  }
  return "500"
})

const community = useList<AcNotification<any, any>>(
  "communityNotifications" + "__" + flatten(props.username),
  {
    grow: true,
    prependNew: true,
    endpoint: `/api/profiles/account/${props.username}/notifications/community/`,
    socketSettings: {
      appLabel: "lib",
      modelName: "Notification",
      serializer: "NotificationSerializer",
      list: {
        appLabel: "profiles",
        modelName: "User",
        pk: `${subject.value.id}`,
        listName: "community_notifications",
      },
    },
  },
)

const sales = useList<AcNotification<any, any>>(
  "salesNotifications" + "__" + flatten(props.username),
  {
    grow: true,
    prependNew: true,
    endpoint: `/api/profiles/account/${props.username}/notifications/sales/`,
    socketSettings: {
      appLabel: "lib",
      modelName: "Notification",
      serializer: "NotificationSerializer",
      list: {
        appLabel: "profiles",
        modelName: "User",
        pk: `${subject.value.id}`,
        listName: "sales_notifications",
      },
    },
  },
)

const { setError } = useErrorHandling()
community.firstRun().catch(setError)
sales.firstRun().catch(setError)

// This might be already defined if we're the current user-- it would be handled by AcNotificationIndicator.
const stats = useSingle<NotificationStats>(
  "notifications_stats__" + flatten(props.username),
  {
    endpoint: `/api/profiles/account/${props.username}/notifications/unread/`,
    x: {
      count: 0,
      community_count: 0,
      sales_count: 0,
    },
  },
)
// The stats update loop is in AcNotificationIndicator. We don't update it here because then we'd have two loops, and
// we don't really need the stats when a staffer is viewing someone else's notifications.
const counts = computed(() => stats.x as NotificationStats)
watch(
  () => subject.value?.artist_mode ?? false,
  (toggle: boolean) => {
    section.value = toggle ? 1 : 0
  },
  { immediate: true },
)

const readUrl = computed(
  () => `/api/profiles/account/${props.username}/notifications/mark-read/`,
)

const markAllRead = () => {
  artCall({
    url: readUrl.value,
    method: "post",
  }).then(() => {
    stats.refresh()
    community.list.map((controller) => {
      controller.x!.read = true
    })
    sales.list.map((controller) => {
      controller.x!.read = true
    })
  })
}
</script>
