<template>
  <v-list-item>
    <router-link :to="{name: 'Submission', params: {assetID: event.target.id}}">
      <v-badge left overlap :value="!notification.read">
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-item-avatar>
          <img :src="$img(event.target, 'notification', true)" alt="">
        </v-list-item-avatar>
      </v-badge>
    </router-link>
    <v-list-item-content>
      <v-list-item-title>
        Tags have been added
      </v-list-item-title>
      <v-list-item-subtitle>
        to your submission<span v-if="event.target.title"> titled
          <router-link :to="{name: 'Submission', params: {'assetID': event.target.id}}">
            '{{event.target.title}}'
          </router-link>:
      </span>
      </v-list-item-subtitle>
      <v-list-item-subtitle>
        <span v-if="tags.length">
          <span
              v-for="tag in event.data.tags" :key="tag"
          >{{tag}}</span>
        </span>
        <span v-else>
          The tags appear to have since been removed.
        </span>
      </v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-submission-tag',
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    tags() {
      if (!(this.event.data.tags && this.event.data.tags.length)) {
        return []
      }
      if (!this.event.target) {
        return []
      }
      const currentTags = this.event.target.tags.map((x) => x.name)
      const shownTags = []
      for (const tag of this.event.data.tags) {
        if (currentTags.indexOf(tag) !== -1) {
          shownTags.push(tag)
        }
      }
      return shownTags
    },
    hidden() {
      return !this.tags.length
    },
  },
}
</script>
