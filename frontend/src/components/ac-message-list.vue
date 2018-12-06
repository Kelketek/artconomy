<template>
  <v-container>
    <v-layout wrap v-if="response !== null && !growing.length">
      <v-flex xs12 text-xs-center class="mt-2">
        <p>There are no messages at this time.</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
      <v-flex xs12 md10 offset-md1 v-if="growing && growing.length">
        <v-list two-line>
          <template v-for="(message, index) in growing">
            <router-link :to="{name: 'Message', params: {username, messageID: message.id}}">
              <v-list-tile avatar>
                <v-list-tile-avatar>
                  <v-badge left overlap>
                    <span slot="badge" v-if="!message.read">*</span>
                    <v-avatar>
                      <img :src="message.sender.avatar_url">
                    </v-avatar>
                  </v-badge>
                </v-list-tile-avatar>
                <v-list-tile-content>
                  <v-list-tile-title>Subject: {{message.subject}}</v-list-tile-title>
                  <v-list-tile-sub-title v-if="isSender">
                    To {{recipients(message) }} On {{formatDateTime(message.created_on)}}
                  </v-list-tile-sub-title>
                  <v-list-tile-sub-title v-else>
                    From {{message.sender.username }} On {{formatDateTime(message.created_on)}}
                  </v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile>
            </router-link>
            <v-divider v-if="index + 1 < growing.length" :key="`divider-${index}`" />
          </template>
        </v-list>
      </v-flex>
      <v-flex xs12>
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1" />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcAvatar from './ac-avatar'
  import {formatDateTime} from '../lib'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  export default {
    name: 'ac-message-list',
    components: {AcAvatar},
    mixins: [Paginated, Viewer, Perms],
    props: ['endpoint', 'isSender'],
    data () {
      return {url: this.endpoint}
    },
    methods: {
      moreNotifications (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      },
      recipients (message) {
        return message.recipients.map((x) => {return x.username}).join(', ')
      },
      formatDateTime: formatDateTime
    }
  }
</script>

<style scoped>

</style>