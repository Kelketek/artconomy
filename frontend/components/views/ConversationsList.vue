<template>
  <v-row no-gutters>
    <v-col v-if="conversations.ready">
      <v-container>
        <v-row no-gutters  >
          <v-col cols="12">
            <ac-paginated :list="conversations" :auto-run="false" :track-pages="true">
              <v-card v-slot="empty">
                <v-card-text>
                  <v-col class="text-center" >
                    <p>You have no conversations at this time.</p>
                    <v-btn color="primary" v-if="isCurrent" @click="showNew = true">Start a Conversation</v-btn>
                  </v-col>
                </v-card-text>
              </v-card>
              <template v-slot:default>
                <v-col>
                  <v-list three-line>
                    <template v-for="(conversation, index) in conversations.list">
                      <v-list-item :key="conversation.id" :to="{name: 'Conversation', params: {username, conversationId: conversation.x.id}}">
                        <v-list-item-avatar>
                          <img :src="avatarImage(conversation.x)"/>
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>{{conversationTitle(conversation.x)}}</v-list-item-title>
                          <v-list-item-subtitle>{{conversation.x.last_comment.user.username}}: {{textualize(conversation.x.last_comment.text)}}</v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                      <v-divider :key="'divider' + conversation.x.id" v-if="index + 1 !== conversations.list.length"></v-divider>
                    </template>
                  </v-list>
                </v-col>
              </template>
            </ac-paginated>
          </v-col>
        </v-row>
      </v-container>
      <ac-add-button v-model="showNew" v-if="isCurrent">Start New Conversation</ac-add-button>
      <ac-form-dialog
          v-model="showNew"
          v-if="isCurrent"
          v-bind="newConversation.bind"
          @submit="newConversation.submitThen(visitConversation)"
          title="Start a New Conversation"
      >
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
          <ac-bound-field
              field-type="ac-user-select" :field="newConversation.fields.participants" label="Start conversation with..." autofocus
          ></ac-bound-field>
        </v-col>
      </ac-form-dialog>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '../../mixins/subjective'
import {ListController} from '@/store/lists/controller'
import {Conversation} from '@/types/Conversation'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import Formatting from '@/mixins/formatting'
import {posse} from '@/lib/lib'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import AcAddButton from '@/components/AcAddButton.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
  @Component({
    components: {AcPaginated, AcFormDialog, AcBoundField, AcAddButton, AcLoadingSpinner, AcAvatar},
  })
export default class ConversationsList extends mixins(Subjective, Formatting) {
    public conversations: ListController<Conversation> = null as unknown as ListController<Conversation>
    public newConversation: FormController = null as unknown as FormController
    public showNew = false
    public privateView = true
    public protectedView = true

    public otherParticipants(participants: TerseUser[]) {
      return participants.filter(
        (participant) => participant.username !== this.username
      )
    }

    public avatarImage(conversation: Conversation) {
      const participants = this.otherParticipants(conversation.participants)
      if (!participants.length) {
        return conversation.participants[0].avatar_url
      }
      return participants[0].avatar_url
    }

    // noinspection JSMethodCanBeStatic
    public conversationTitle(conversation: Conversation) {
      const participants = this.otherParticipants(conversation.participants)
      if (!participants.length) {
        return '(Abandoned Conversation)'
      }
      return posse(participants.map((participant) => participant.username), this.participantsCount(participants))
    }

    // noinspection JSMethodCanBeStatic
    public participantsCount(participants: TerseUser[]) {
      let participantsCount = participants.length
      participantsCount -= 3
      if (participantsCount < 0) {
        participantsCount = 0
      }
      return participantsCount
    }

    public visitConversation(conversation: Conversation) {
      this.$router.push({name: 'Conversation', params: {username: this.username, conversationId: conversation.id + ''}})
    }

    public created() {
      this.conversations = this.$getList('conversations-' + this.username, {
        endpoint: `/api/profiles/v1/account/${this.username}/conversations/`,
      })
      this.newConversation = this.$getForm('new-conversation', {
        fields: {participants: {value: []}},
        endpoint: `/api/profiles/v1/account/${this.rawViewerName}/conversations/`,
      })
      this.conversations.firstRun().catch(this.setError)
    }
}
</script>
