<template>
  <v-list-tile avatar>
    <router-link :to="assetLink">
      <v-badge left overlap>
        <span slot="badge" v-if="notification.unread">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <slot name="title"></slot>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        <slot name="subtitle"></slot>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-base-notification',
    mixins: [Notification],
    props: ['assetLink']
  }
</script>

<style scoped>

</style>