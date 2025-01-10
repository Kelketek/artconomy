<template>
  <v-row no-gutters>
    <v-col v-if="conversations.ready">
      <v-container>
        <v-row no-gutters>
          <v-col cols="12" class="text-center text-md-right py-2" v-if="isCurrent">
            <v-btn color="green" @click="showNew = true" variant="elevated">
              <v-icon left :icon="mdiPlus"/>
              New Conversation
            </v-btn>
          </v-col>
          <v-col cols="12">
            <ac-paginated :list="conversations" :auto-run="false" :track-pages="true">
              <template v-slot:empty>
                <v-row>
                  <v-col cols="12">
                    <v-card>
                      <v-card-text>
                        <v-col class="text-center">
                          <p>You have no conversations at this time.</p>
                          <v-btn color="primary" v-if="isCurrent" @click="showNew = true" variant="flat">Start a Conversation</v-btn>
                        </v-col>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </template>
              <template v-slot:default>
                <v-col>
                  <v-list three-line>
                    <template v-for="(conversation, index) in conversations.list" :key="conversation.x!.id">
                      <v-list-item :to="{name: 'Conversation', params: {username, conversationId: conversation.x!.id}}" v-if="conversation.x">
                        <template v-slot:prepend>
                          <img :src="avatarImage(conversation.x!)" alt=""/>
                        </template>
                        <v-list-item-title>{{conversationTitle(conversation.x!)}}</v-list-item-title>
                        <v-list-item-subtitle v-if="conversation.x!.last_comment">
                          <span v-if="conversation.x!.last_comment.user">{{conversation.x!.last_comment.user.username}}:</span>
                          {{textualize(conversation.x!.last_comment.text)}}
                        </v-list-item-subtitle>
                      </v-list-item>
                      <v-divider :key="'divider' + conversation.x!.id"
                                 v-if="index + 1 !== conversations.list.length"></v-divider>
                    </template>
                  </v-list>
                </v-col>
              </template>
            </ac-paginated>
          </v-col>
        </v-row>
      </v-container>
      <ac-form-dialog
          v-model="showNew"
          v-if="isCurrent"
          v-bind="newConversation.bind"
          @submit="newConversation.submitThen(visitConversation)"
          title="Start a New Conversation"
      >
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
          <v-row>
            <v-col cols="12">
              <ac-bound-field
                  field-type="ac-user-select" :field="newConversation.fields.participants"
                  label="Start conversation with..." autofocus
              />
            </v-col>
            <v-col cols="12">
              <ac-bound-field
                  field-type="ac-captcha-field" :field="newConversation.fields.captcha" label="Prove you are human"
              />
            </v-col>
          </v-row>
        </v-col>
      </ac-form-dialog>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {mdiPlus} from '@mdi/js'
import {posse} from '@/lib/otherFormatters.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {textualize} from '@/lib/markdown.ts'
import type {Conversation, SubjectiveProps} from '@/types/main'
import type {StaffPower, TerseUser} from '@/store/profiles/types/main'


const props = defineProps<SubjectiveProps>()
const router = useRouter()
const {rawViewerName} = useViewer()
const {setError} = useErrorHandling()
const {isCurrent} = useSubject({ props, privateView: true, controlPowers: ['view_as'] as StaffPower[] })
const showNew = ref(false)

const conversations = useList<Conversation>('conversations-' + props.username, {
  endpoint: `/api/profiles/account/${props.username}/conversations/`,
})
const newConversation = useForm('new-conversation', {
  fields: {
    participants: {value: []},
    captcha: {value: ''},
  },
  endpoint: `/api/profiles/account/${rawViewerName.value}/conversations/`,
})
conversations.firstRun().catch(setError)

const otherParticipants = (participants: TerseUser[]) => {
  return participants.filter(
      (participant) => participant.username !== props.username,
  )
}

const avatarImage = (conversation: Conversation) => {
  const participants = otherParticipants(conversation.participants)
  if (!participants.length) {
    return conversation.participants[0].avatar_url
  }
  return participants[0].avatar_url
}

const conversationTitle = (conversation: Conversation) => {
  const participants = otherParticipants(conversation.participants)
  if (!participants.length) {
    return '(Abandoned Conversation)'
  }
  return posse(participants.map((participant) => participant.username), participantsCount(participants))
}

const participantsCount = (participants: TerseUser[]) => {
  let participantsCount = participants.length
  participantsCount -= 3
  if (participantsCount < 0) {
    participantsCount = 0
  }
  return participantsCount
}

const visitConversation = (conversation: Conversation) => {
  router.push({
    name: 'Conversation',
    params: {
      username: props.username,
      conversationId: conversation.id + '',
    },
  })
}
</script>
