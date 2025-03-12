<template>
  <ac-base-notification
    :notification="notification"
    :asset-link="characterLink"
    :username="username"
  >
    <template #title>
      <ac-link :to="characterLink"> A character was shared with you </ac-link>
    </template>
    <template #subtitle>
      <ac-link :to="characterLink">
        "{{ event.data.character.name }}" was shared by
        {{ event.data.user.username }}
      </ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {
  DisplayData,
  NotificationProps,
  useEvent,
} from "../mixins/notification.ts"
import AcLink from "@/components/wrappers/AcLink.vue"
import AcBaseNotification from "@/components/views/notifications/events/AcBaseNotification.vue"
import { computed } from "vue"

import { TerseUser } from "@/store/profiles/types/main"
import { Character } from "@/store/characters/types/main"

declare interface CharShared extends DisplayData {
  character: Character
  user: TerseUser
}

const props = defineProps<NotificationProps<Character, CharShared>>()
const event = useEvent(props)
const characterLink = computed(() => {
  if (event.value.data.character) {
    return {
      name: "Character",
      params: {
        characterName: event.value.data.character.name,
        username: event.value.data.character.user.username,
      },
    }
  } else {
    return {}
  }
})
</script>

<style scoped></style>
