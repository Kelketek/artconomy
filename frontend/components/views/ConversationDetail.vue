<template>
  <v-row no-gutters :key="conversationId">
    <v-col v-if="conversation.x">
      <v-container>
        <v-card>
          <v-row>
            <v-col class="shrink"
                   v-for="participant in conversation.x.participants.filter((x) => x.username !== rawViewerName)"
                   :key="participant.id">
              <ac-avatar
                  :user="participant"
                  class="px-1"
              />
            </v-col>
            <v-spacer/>
            <v-col class="shrink d-flex" align-self="center">
              <ac-confirmation :action="leaveConversation">
                <template v-slot:default="{on}">
                  <v-btn icon v-on="on" color="red" class="delete-button" aria-label="Delete Conversation">
                    <v-icon icon="mdi-delete"/>
                  </v-btn>
                </template>
                <template v-slot:confirmation-text>
                  <v-col>
                    Are you sure you wish to leave this conversation? This cannot be undone. Conversations are deleted
                    when all users have left.
                  </v-col>
                </template>
              </ac-confirmation>
            </v-col>
          </v-row>
        </v-card>
      </v-container>
      <ac-loading-spinner v-if="!conversation.x"/>
      <v-container>
        <v-row no-gutters>
          <v-col cols="12">
            <p><strong class="danger">WARNING:</strong> Do not discuss order details through private conversations. Add
              any details
              about the commission you want in an order. You can negotiate details and pricing and approve/disapprove as
              needed within the order itself.
              Requirements negotiated within a private conversation cannot be enforced by
              <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">Artconomy Shield</router-link>&nbsp;
              <router-link :to="{name: 'BuyAndSell', params: {question: 'disputes'}}">dispute resolution.</router-link>
            </p>
          </v-col>
        </v-row>
      </v-container>
      <v-container fluid class="pa-0">
        <ac-comment-section
            :commentList="conversationComments"
            :nesting="false"
            :locked="(!inConversation) && locked">
          <template v-slot:empty>
            <v-col class="text-center pt-1">
              <v-col>
                <h2>Start a conversation</h2>
                <p>
                  Enter some text into the field below to start messaging!
                </p>
              </v-col>
            </v-col>
          </template>
        </ac-comment-section>
        <v-row no-gutters>
          <v-col class="text-center" cols="12" v-if="!inConversation">
            <v-btn @click="locked = !locked" :block="$vuetify.display.xs" class="lock-toggle" variant="flat">
              <v-icon v-if="locked" left icon="mdi-lock"/>
              <v-icon v-else left icon="mdi-lock-open"/>
              <span v-if="locked">Unlock to allow outside comment.</span>
              <span v-else>Lock to prevent outside comment.</span>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import Formatting from '@/mixins/formatting.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {Conversation} from '@/types/Conversation.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import {ListController} from '@/store/lists/controller.ts'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'

@Component({
  components: {
    AcConfirmation,
    AcLoadingSpinner,
    AcCommentSection,
    AcAvatar,
  },
})
class ConversationDetail extends mixins(Subjective, Formatting) {
  @Prop()
  public conversationId!: string

  public conversation: SingleController<Conversation> = null as unknown as SingleController<Conversation>
  public conversationComments: ListController<Comment> = null as unknown as ListController<Comment>
  public locked = true

  public goBack() {
    this.$router.push({
      name: 'Conversations',
      params: {username: this.username},
    })
  }

  public get inConversation() {
    /* istanbul ignore next */
    if (!this.conversation.x) {
      return
    }
    return this.conversation.x.participants.map((user) => user.username).indexOf(this.rawViewerName) !== -1
  }

  public created() {
    this.conversation = this.$getSingle('conversation-' + this.conversationId, {endpoint: this.url})
    this.conversation.get().catch(this.setError)
    this.conversationComments = this.$getList(
        'conversation-' + this.conversationId + '-comments',
        {
          endpoint: `/api/lib/comments/profiles.Conversation/${this.conversationId}/`,
          reverse: true,
          grow: true,
          params: {size: 5},
        },
    )
  }

  public get url(): string {
    return `/api/profiles/account/${this.username}/conversations/${this.conversationId}/`
  }

  public leaveConversation() {
    return this.conversation.delete().then(this.goBack)
  }
}

export default toNative(ConversationDetail)
</script>

<style scoped>

</style>
