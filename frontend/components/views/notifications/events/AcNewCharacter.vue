<template>
  <ac-base-notification :notification="notification" :asset-link="characterLink" :username="username">
    <template v-slot:title>
      <ac-link
          :to="characterLink">New Character: {{event.data.character.name}}
      </ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link
          :to="characterLink">By {{event.data.character.user.username}}
      </ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import AcBaseNotification from './AcBaseNotification.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {
  DisplayData,
  NotificationProps,
  NotificationUser,
  useEvent,
} from '@/components/views/notifications/mixins/notification.ts'
import {Character} from '@/store/characters/types/Character.ts'
import {computed} from 'vue'

declare interface NewCharacter extends DisplayData {
  character: Character,
}
const props = defineProps<NotificationProps<NotificationUser, NewCharacter>>()
const event = useEvent(props)

const characterLink = computed(() => ({
    name: 'Character',
    params: {
      username: event.value.data.character.user.username,
      characterName: event.value.data.character.name,
    },
  }
))
</script>

<style scoped>

</style>
