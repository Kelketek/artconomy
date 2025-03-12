<template>
  <v-btn
    variant="plain"
    class="notifications-button"
    aria-label="Notifications"
  >
    <template #default>
      <v-badge overlap right color="red" :model-value="!!counts.count">
        <template #badge>
          <span v-if="counts.count && counts.count < 1000">{{
            counts.count
          }}</span>
          <span v-else>*</span>
        </template>
        <v-icon size="x-large" :icon="mdiBell" />
      </v-badge>
    </template>
  </v-btn>
</template>
<script setup lang="ts">
import { mdiBell } from "@mdi/js"
import { useSingle } from "@/store/singles/hooks.ts"
import { computed } from "vue"
import { flatten } from "@/lib/lib.ts"
import type { NotificationStats, SubjectiveProps } from "@/types/main"

const props = defineProps<SubjectiveProps>()
const stats = useSingle<NotificationStats>(
  "notifications_stats__" + flatten(props.username),
  {
    endpoint: `/api/profiles/account/${props.username}/notifications/unread/`,
    x: {
      count: 0,
      community_count: 0,
      sales_count: 0,
    },
    socketSettings: {
      serializer: "UnreadNotificationsSerializer",
      appLabel: "profiles",
      modelName: "User",
    },
  },
)
const counts = computed(() => stats.x as NotificationStats)
stats.get()
</script>
