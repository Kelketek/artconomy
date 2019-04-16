<template>
  <v-list-tile avatar>
    <router-link v-if="event.data.character" :to="{name: 'Submission', params: {assetID: event.target.id}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.target, 'notification', true)" alt="">
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-badge left v-else overlap>
      <span slot="badge" v-if="!notification.read">*</span>
      <v-list-tile-avatar>
        <img :src="$img(event.target.primary_asset, 'notification', true)" alt="">
      </v-list-tile-avatar>
    </v-badge>
    <v-list-tile-content>
      <v-list-tile-title>
        <span v-if="event.data.character">{{event.data.character.name}}</span>
        <span v-else>A removed character</span>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        was tagged in your submission titled '{{event.target.title}}'
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action>
      <router-link
          :to="{name: 'Character', params: {character: event.data.character.name, username: event.data.character.user.username}}">
        <v-avatar>
          <img :src="$img(event.data.character.primary_asset, 'notification', true)" alt="">
        </v-avatar>
      </router-link>
    </v-list-tile-action>
  </v-list-tile>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-submission-char-tag',
  mixins: [Notification],
}
</script>
