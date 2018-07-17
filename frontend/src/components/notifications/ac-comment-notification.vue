<template>
  <v-list-tile avatar>
    <router-link :to="event.data.link" v-if="event.data.link">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-badge v-else left overlap>
      <span slot="badge" v-if="!notification.read">*</span>
      <v-list-tile-avatar>
        <img :src="$img(event.data.display, 'notification', true)" >
      </v-list-tile-avatar>
    </v-badge>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="event.data.link" v-if="event.data.link">
          {{titleText}}
        </router-link>
        <span v-else>{{titleText}}</span>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        on <router-link :to="event.data.link" v-if="event.data.link">{{event.data.name}}</router-link><span v-else>'{{event.data.name}}'</span>
      </v-list-tile-sub-title>
      <v-list-tile-sub-title>
        by {{commenters}}
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import AcAsset from '../ac-asset'
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-comment-notification',
    components: {AcAsset},
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      commenters () {
        let commenters = this.event.data.commenters.join(', ')
        if (this.event.data.additional) {
          commenters += ' and ' + this.event.data.additional
          if (this.event.data.additional === 1) {
            commenters += ' other'
          } else {
            commenters += ' others'
          }
        }
        return commenters
      },
      titleText () {
        if (this.event.data.is_thread) {
          return 'A comment has been added to a thread'
        }
        return 'A comment has been added'
      }
    }
  }
</script>