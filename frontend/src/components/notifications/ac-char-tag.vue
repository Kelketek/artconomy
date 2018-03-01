<template>
  <v-list-tile avatar>
    <router-link v-if="event.data.asset" :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.target.primary_asset, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-badge left v-else overlap>
      <span slot="badge" v-if="!notification.read">*</span>
      <v-list-tile-avatar>
        <img :src="$img(event.target.primary_asset, 'notification', true)" >
      </v-list-tile-avatar>
    </v-badge>
    <v-list-tile-content>
      <v-list-tile-title>{{event.target.name}} was tagged in a submission</v-list-tile-title>
      <v-list-tile-sub-title>
        <span v-if="event.data.user">by {{event.data.user.username}}</span>
        <span v-else>by a removed user</span>
        <span v-if="event.data.asset">titled
          <router-link :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">'{{event.data.asset.title}}'.</router-link>
        </span>
        <span v-else> but the submission was removed.</span>
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action>
      <router-link :to="{name: 'Submission', params: {assetID: event.data.asset.id}}" v-if="event.data.asset">
        <v-avatar>
          <img :src="$img(event.data.asset, 'notification', true)">
        </v-avatar>
      </router-link>
    </v-list-tile-action>
  </v-list-tile>
</template>

<style scoped>
  .notification-preview {
    width: 80px;
    height: 80px;
  }
</style>

<script>
  import AcAsset from '../ac-asset'
  import Notification from '../../mixins/notification'

  export default {
    name: 'ac-char-tag',
    mixins: [Notification],
    components: {
      AcAsset
    }
  }
</script>