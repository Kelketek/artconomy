<template>
  <v-list-item>
    <router-link v-if="event.data.character" :to="{name: 'Submission', params: {assetID: event.target.id}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-item-avatar>
          <img :src="$img(event.target, 'notification', true)" alt="">
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
      <v-list-item-title>
        <span v-if="event.data.character">{{event.data.character.name}}</span>
        <span v-else>A removed character</span>
      </v-list-item-title>
      <v-list-item-subtitle>
        was tagged in your submission titled '{{event.target.title}}'
      </v-list-item-subtitle>
    </v-list-item-content>
    <v-list-item-action>
      <router-link
          :to="{name: 'Character', params: {character: event.data.character.name, username: event.data.character.user.username}}">
        <v-avatar>
          <img :src="$img(event.data.character.primary_asset, 'notification', true)" alt="">
        </v-avatar>
      </router-link>
    </v-list-item-action>
  </v-list-item>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-submission-char-tag',
  mixins: [Notification],
}
</script>
