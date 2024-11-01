<template>
  <ac-base-notification :notification="notification" :asset-link="event.data.link" :username="username">
    <template v-slot:title>
      <ac-link :to="event.data.link">{{titleText}}</ac-link>
    </template>
    <template v-slot:subtitle>
      <ac-link :to="event.data.link">{{byLine}}</ac-link>
    </template>
  </ac-base-notification>
</template>

<script setup lang="ts">
import {DisplayData, NotificationProps, useEvent} from '../mixins/notification.ts'
import AcBaseNotification from './AcBaseNotification.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {posse} from '@/lib/otherFormatters.ts'
import {RouteLocationRaw} from 'vue-router'
import {computed} from 'vue'
import {TerseUser} from '@/store/profiles/types/main'

declare interface CommentNotification extends DisplayData {
  link: RouteLocationRaw,
  subject: TerseUser,
  commenters: string[],
  additional: number,
  is_thread: boolean,
  name: string,
}

const props = defineProps<NotificationProps<null, CommentNotification>>()
const event = useEvent(props)

const byLine = computed(() => {
  let commenters = ''
  if (event.value.data.subject) {
    commenters += 'from '
  } else {
    commenters += 'by '
  }
  commenters += posse(event.value.data.commenters, event.value.data.additional)
  return commenters
})
const titleText = computed(() => {
  let message
  if (event.value.data.is_thread) {
    message = 'A comment has been added to a thread in '
  } else {
    message = 'A comment has been added in '
  }
  return message + event.value.data.name
})
</script>
