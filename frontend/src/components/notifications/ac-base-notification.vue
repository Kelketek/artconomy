<template>
  <v-list-tile avatar>
    <a :href="hrefLink" v-if="hrefLink">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <slot name="avatar">
            <img :src="event.data.display.avatar_url" v-if="event.data.display && event.data.display.avatar_url">
            <img :src="$img(event.data.display, 'notification', true)" v-else>
          </slot>
        </v-list-tile-avatar>
      </v-badge>
    </a>
    <router-link :to="assetLink" v-else>
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <slot name="avatar">
            <img :src="event.data.display.avatar_url" v-if="event.data.display && event.data.display.avatar_url">
            <img :src="$img(event.data.display, 'notification', true)" v-else>
          </slot>
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
    props: ['assetLink', 'hrefLink']
  }
</script>

<style scoped>

</style>