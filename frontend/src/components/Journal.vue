<template>
  <div>
    <v-container v-if="journal">
      <v-card>
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs12 sm3 md2 text-xs-center class="pl-1 pr-1">
              <p>From:</p>
              <ac-avatar :user="journal.user" />
            </v-flex>
            <v-flex xs12 sm9 md10 class="pt-1 pl-1 pr-1">
              <v-flex xs12 class="title">
                <ac-patchfield v-model="journal.subject" name="subject" :editmode="editing" styleclass="h1" :url="url" />
              </v-flex>
              <v-flex xs12 class="mt-2 pl-1 pr-1">
                <ac-patchfield v-model="journal.body" :multiline="true" name="body" :editmode="editing" :url="url" />
              </v-flex>
            </v-flex>
            <v-flex xs12 sm3 md2 text-xs-center class="pl-1 pr-1">
              <v-card-title class="clickable" v-if="editing && isCurrent" @click="editing=false"><v-icon>lock_open</v-icon></v-card-title>
              <v-card-title class="clickable" v-else-if="isCurrent" @click="editing=true"><v-icon>lock</v-icon></v-card-title>
            </v-flex>
            <v-flex text-xs-right>
              <ac-action :url="url" :send="{subscribed: !journal.subscribed}" method="PUT" :success="populateJournal" v-if="isLoggedIn">
                <v-icon v-if="journal.subscribed">volume_up</v-icon><v-icon v-else>volume_off</v-icon>
              </ac-action>
              <ac-action v-if="isCurrent" :url="url" method="PATCH" :send="{comments_disabled: !journal.comments_disabled}" :success="populateJournal">
                <span v-if="journal.comments_disabled">Enable Comments</span>
                <span v-else>Disable Comments</span>
              </ac-action>
              <ac-action color="red" :url="url" method="DELETE" :confirm="true" :success="goBack" v-if="isCurrent">
                <v-icon>delete</v-icon>
                <div class="text-left" slot="confirmation-text">
                  Are you sure you want to delete this journal? This cannot be undone.
                </div>
              </ac-action>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-container>
    <v-container fluid v-if="journal">
      <v-layout row wrap>
        <v-flex xs12>
          <ac-comment-section :commenturl="commenturl" :nesting="false" :locked="journal.comments_disabled" />
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>
<script>
  import {artCall} from '../lib'
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  import Editable from '../mixins/editable'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'

  export default {
    components: {AcAvatar, AcCommentSection},
    props: ['journalID'],
    mixins: [Perms, Viewer, Editable],
    data () {
      return {
        journal: null,
        url: `/api/profiles/v1/account/${this.username}/journals/${this.journalID}/`,
        commenturl: `/api/profiles/v1/account/${this.username}/journals/${this.journalID}/comments/`
      }
    },
    methods: {
      populateJournal (response) {
        this.journal = response
      },
      goBack () {
        this.$router.history.push({name: 'Profile', params: {username: this.username}})
      }
    },
    created () {
      artCall(this.url, 'GET', undefined, this.populateJournal, this.$error)
    }
  }
</script>