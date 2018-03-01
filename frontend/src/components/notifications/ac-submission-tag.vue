<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Submission', params: {assetID: event.target.id}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.target, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        Tags have been added
      </v-list-tile-title>
      <v-list-tile-sub-title>
          to your submission<span v-if="event.target.title"> titled
          <router-link :to="{name: 'Submission', params: {'assetID': event.target.id}}">
            '{{event.target.title}}'
          </router-link>:
      </span>
      </v-list-tile-sub-title>
      <v-list-tile-sub-title>
        <span v-if="tags.length">
          <span
              v-for="tag in event.data.tags"
          >{{tag}}</span>
        </span>
        <span v-else>
          The tags appear to have since been removed.
        </span>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import AcAsset from '../ac-asset'
  import AcTag from '../ac-tag'
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-submission-tag',
    components: {
      AcTag,
      AcAsset
    },
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      tags () {
        if (!(this.event.data.tags && this.event.data.tags.length)) {
          return []
        }
        if (!this.event.target) {
          return []
        }
        let currentTags = this.event.target.tags.map(x => x.name)
        let shownTags = []
        for (let tag of this.event.data.tags) {
          if (currentTags.indexOf(tag) !== -1) {
            shownTags.push(tag)
          }
        }
        return shownTags
      },
      hidden () {
        return !this.tags.length
      }
    }
  }
</script>