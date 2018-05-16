<template>
  <div>
    <v-container>
      <v-card v-if="message">
        <v-layout row wrap>
          <v-flex xs12 sm3 md2 text-xs-center class="pl-1 pr-1">
            <p>From:</p>
            <ac-avatar :user="message.sender" />
          </v-flex>
          <v-flex xs12 sm9 md10 class="pt-1 pl-1 pr-1">
            <v-flex xs12 class="title">
             <ac-patchfield v-model="message.subject" name="subject" :editmode="editing" styleclass="h1" :url="url" />
            </v-flex>
            <v-flex xs12 class="mt-2 pl-1 pr-1">
              <ac-patchfield v-model="message.body" :multiline="true" name="body" :editmode="editing" :url="url" />
            </v-flex>
          </v-flex>
          <v-flex xs12 sm3 md2 text-xs-center class="pl-1 pr-1">
            <v-card-title class="clickable" v-if="editing && isSender" @click="editing=false"><v-icon>lock_open</v-icon></v-card-title>
            <v-card-title class="clickable" v-else-if="isSender" @click="editing=true"><v-icon>lock</v-icon></v-card-title>
          </v-flex>
          <v-flex xs12 sm9 md10 class="pl-1 pr-1">
            <v-flex xs12>Recipients:</v-flex>
            <v-flex xs12 class="mt-1">
              <ac-avatar v-for="recipient in message.recipients" :key="recipient.id" :user="recipient"/>
            </v-flex>
          </v-flex>
          <v-flex text-xs-right>
            <ac-action color="red" :url="`${url}leave/`" :confirm="true" :success="goBack">
              Leave Conversation
              <div class="text-left" slot="confirmation-text">
                Are you sure you want to leave this conversation? This cannot be undone. Note: Conversations are deleted
                when all participants have left.
              </div>
            </ac-action>
          </v-flex>
        </v-layout>
      </v-card>
    </v-container>
    <v-container fluid>
      <v-layout row wrap>
        <v-flex xs12>
          <ac-comment-section :commenturl="commenturl" :nesting="false" />
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import Viewer from '../mixins/viewer'
  import {artCall} from '../lib'
  import AcAvatar from './ac-avatar'
  import AcCommentSection from './ac-comment-section'
  export default {
    name: 'Message',
    components: {AcCommentSection, AcAvatar},
    mixins: [Viewer, Perms, Editable],
    props: ['messageID'],
    data () {
      return {
        message: null,
        url: `/api/profiles/v1/messages/${this.messageID}/`,
        commenturl: `/api/profiles/v1/messages/${this.messageID}/comments/`
      }
    },
    methods: {
      populateMessage (response) {
        this.message = response
      },
      goBack () {
        this.$router.history.push({name: 'Messages', params: {username: this.username}})
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateMessage, this.$error)
    },
    computed: {
      isSender () {
        return this.message.sender.username === this.viewer.username
      }
    }
  }
</script>

<style scoped>

</style>