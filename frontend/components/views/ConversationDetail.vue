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
                    <v-icon :icon="mdiDelete"/>
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
            <v-btn @click="locked = !locked" :block="xs" class="lock-toggle" variant="flat">
              <v-icon v-if="locked" left :icon="mdiLock"/>
              <v-icon v-else left :icon="mdiLockOpen"/>
              <span v-if="locked">Unlock to allow outside comment.</span>
              <span v-else>Lock to prevent outside comment.</span>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import {Conversation} from '@/types/Conversation.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import Comment from '@/types/Comment.ts'
import {mdiLock, mdiDelete, mdiLockOpen} from '@mdi/js'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {computed, ref} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useRouter} from 'vue-router'
import {useViewer} from '@/mixins/viewer.ts'
import {useDisplay} from 'vuetify'


const props = defineProps<SubjectiveProps & {conversationId: number}>()
const router = useRouter()
const {rawViewerName} = useViewer()
const {setError} = useErrorHandling()
const locked = ref(true)
const {xs} = useDisplay()

const url = computed(() => {
  return `/api/profiles/account/${props.username}/conversations/${props.conversationId}/`
})
const conversation = useSingle<Conversation>('conversation-' + props.conversationId, {endpoint: url.value})
conversation.get().catch(setError)
const conversationComments = useList<Comment>(
    'conversation-' + props.conversationId + '-comments',
    {
      endpoint: `/api/lib/comments/profiles.Conversation/${props.conversationId}/`,
      reverse: true,
      grow: true,
      params: {size: 5},
    },
)

const goBack = () => {
  router.push({
    name: 'Conversations',
    params: {username: props.username},
  })
}

const leaveConversation = () => {
  return conversation.delete().then(goBack)
}

const inConversation = computed(() => {
  /* istanbul ignore next */
  if (!conversation.x) {
    return
  }
  return conversation.x.participants.map((user) => user.username).indexOf(rawViewerName.value) !== -1
})
</script>

<style scoped>

</style>
