<template>
  <v-list-item>
    <v-list-item-action>
    <ac-link :to="assetLink">
      <v-badge left overlap :value="!notification.read">
        <template v-slot:badge>
          <span>*</span>
        </template>
        <slot name="avatar">
          <v-avatar>
            <img :src="event.data.display.avatar_url" v-if="event.data.display && event.data.display.avatar_url" alt="">
            <img :src="$img(event.data.display, 'notification', true)" alt="" v-else>
          </v-avatar>
        </slot>
      </v-badge>
    </ac-link>
    </v-list-item-action>
    <v-list-item-content>
      <v-list-item-title>
        <slot name="title" />
      </v-list-item-title>
      <v-list-item-subtitle>
        <slot name="subtitle" />
      </v-list-item-subtitle>
      <slot name="extra" />
    </v-list-item-content>
  </v-list-item>
</template>

<script>
import Notification from '../mixins/notification'
import AcLink from '@/components/wrappers/AcLink'

export default {
  name: 'ac-base-notification',
  components: {AcLink},
  mixins: [Notification],
  props: ['assetLink', 'hrefLink'],
}
</script>

<style scoped>

</style>
