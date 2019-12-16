<template>
  <v-list-item>
    <router-link v-if="event.data.asset" :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-item-avatar>
          <img :src="$img(event.target.primary_asset, 'notification', true)" alt="">
        </v-list-item-avatar>
      </v-badge>
    </router-link>
    <v-badge left v-else overlap>
      <span slot="badge" v-if="!notification.read">*</span>
      <v-list-item-avatar>
        <img :src="$img(event.target.primary_asset, 'notification', true)" alt="">
      </v-list-item-avatar>
    </v-badge>
    <v-list-item-content>
      <v-list-item-title>{{event.target.name}} was tagged in a submission</v-list-item-title>
      <v-list-item-subtitle>
        <span v-if="event.data.user">by {{event.data.user.username}}</span>
        <span v-else>by a removed user</span>
        <span v-if="event.data.asset">titled
          <router-link
              :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">'{{event.data.asset.title}}'.</router-link>
        </span>
        <span v-else> but the submission was removed.</span>
      </v-list-item-subtitle>
    </v-list-item-content>
    <v-list-item-action>
      <router-link :to="{name: 'Submission', params: {assetID: event.data.asset.id}}" v-if="event.data.asset">
        <v-avatar>
          <img :src="$img(event.data.asset, 'notification', true)" alt="">
        </v-avatar>
      </router-link>
    </v-list-item-action>
  </v-list-item>
</template>

<style scoped>
  .notification-preview {
    width: 80px;
    height: 80px;
  }
</style>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-char-tag',
  mixins: [Notification],
}
</script>
