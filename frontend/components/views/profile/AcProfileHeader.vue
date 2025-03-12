<template>
  <v-toolbar :density="dense ? 'compact' : 'default'" color="black">
    <ac-avatar :username="username" :show-name="false" class="ml-3" />
    <v-toolbar-title class="ml-1">
      <ac-link :to="subject && profileLink(subject)">
        {{ subjectHandler.displayName }}
      </ac-link>
    </v-toolbar-title>
    <v-spacer />
    <v-toolbar-items v-if="subject && isRegistered && display.smAndUp">
      <v-btn
        v-if="showEdit && controls"
        color="secondary"
        variant="flat"
        @click="editing = !editing"
      >
        <v-icon v-if="editing" :icon="mdiLock" />
        <v-icon v-else :icon="mdiPencil" />
        <span v-if="editing">Lock</span>
        <span v-else>Edit</span>
      </v-btn>
      <v-btn
        v-if="powers.view_as && !isCurrent"
        color="secondary"
        variant="flat"
        @click="showMenu = !showMenu"
      >
        <v-icon left :icon="mdiMenu" />
        Menu
      </v-btn>
      <v-btn
        v-if="powers.view_as && !isCurrent"
        color="info"
        variant="flat"
        @click="showNotifications = !showNotifications"
      >
        <v-icon left :icon="mdiMenu" />
        Notifications
      </v-btn>
      <v-btn
        v-if="!isCurrent"
        color="primary"
        class="message-button"
        variant="flat"
        @click="showNew = true"
      >
        <v-icon left :icon="mdiMessage" />
        Message
      </v-btn>
      <v-btn
        v-if="!isCurrent"
        color="grey-darken-2"
        variant="flat"
        @click="subjectHandler.user.patch({ watching: !subject.watching })"
      >
        <v-icon v-if="subject.watching" left :icon="mdiEyeOff" />
        <v-icon v-else left :icon="mdiEye" />
        <span v-if="subject.watching">Unwatch</span>
        <span v-else>Watch</span>
      </v-btn>
      <!--suppress JSCheckFunctionSignatures -->
      <ac-confirmation
        v-if="!isCurrent"
        :action="
          () => subjectHandler.user.patch({ blocking: !subject!.blocking })
        "
      >
        <template #confirmation-text>
          <v-col>
            <v-col v-if="subject!.blocking">
              <p>
                Are you sure you wish to unblock
                {{ subjectHandler.displayName }}? They will be able to message
                you, comment, and perform other interactive actions with your
                account.
              </p>
            </v-col>
            <v-col v-else>
              <p>
                Are you sure you wish to block {{ subjectHandler.displayName }}?
                They will not be able to message you, comment on your items, or
                perform other interactive actions with your account.
              </p>
              <p v-if="subject.watching">
                This will also remove them from your watchlist.
              </p>
            </v-col>
          </v-col>
        </template>
        <template #default="{ on }">
          <v-btn color="red" variant="flat" v-on="on">
            <v-icon left :icon="mdiCancel" />
            <span v-if="subject!.blocking">Unblock</span>
            <span v-else>Block</span>
          </v-btn>
        </template>
      </ac-confirmation>
    </v-toolbar-items>
    <v-menu v-else-if="subject && isRegistered" offset-y>
      <template #activator="activator">
        <v-btn v-bind="activator.props" icon aria-label="Actions">
          <v-icon :icon="mdiDotsHorizontal" />
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item
          v-if="powers.view_as && !isCurrent"
          @click="showMenu = true"
        >
          <template #prepend>
            <v-icon :icon="mdiMenu" />
          </template>
          <v-list-item-title>Menu</v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="powers.view_as && !isCurrent"
          @click="showNotifications = true"
        >
          <template #prepend>
            <v-icon :icon="mdiMenu" />
          </template>
          <v-list-item-title>Notifications</v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="!isCurrent"
          class="message-button"
          @click="showNew = true"
        >
          <template #prepend>
            <v-icon :icon="mdiMessage" />
          </template>
          <v-list-item-title>Message</v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="!isCurrent"
          @click="subjectHandler.user.patch({ watching: !subject.watching })"
        >
          <template #prepend>
            <v-icon v-if="subject.watching" :icon="mdiEyeOff" />
            <v-icon v-else :icon="mdiEye" />
          </template>
          <v-list-item-title>
            <span v-if="subject.watching">Unwatch</span>
            <span v-else>Watch</span>
          </v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="controls && showEdit"
          @click.stop="editing = !editing"
        >
          <template #prepend>
            <v-icon v-if="editing" :icon="mdiLock" />
            <v-icon v-else :icon="mdiPencil" />
          </template>
          <v-list-item-title v-if="editing"> Lock </v-list-item-title>
          <v-list-item-title v-else> Edit </v-list-item-title>
        </v-list-item>
        <ac-confirmation v-if="!isCurrent" :action="async () => blockToggle">
          <template #confirmation-text>
            <v-col>
              <v-col v-if="subject!.blocking">
                <p>
                  Are you sure you wish to unblock
                  {{ subjectHandler.displayName }}? They will be able to message
                  you, comment, and perform other interactive actions with your
                  account.
                </p>
              </v-col>
              <v-col v-else>
                <p>
                  Are you sure you wish to block
                  {{ subjectHandler.displayName }}? They will not be able to
                  message you, comment on your items, or perform other
                  interactive actions with your account.
                </p>
                <p v-if="subject.watching">
                  This will also remove them from your watchlist.
                </p>
              </v-col>
            </v-col>
          </template>
          <template #default="{ on }">
            <v-list-item v-on="on">
              <template #prepend>
                <v-icon :icon="mdiCancel" />
              </template>
              <v-list-item-title>
                <span v-if="subject.blocking">Unblock</span>
                <span v-if="!subject.blocking">Block</span>
              </v-list-item-title>
            </v-list-item>
          </template>
        </ac-confirmation>
      </v-list>
    </v-menu>
    <v-navigation-drawer
      v-if="powers.view_as && subject"
      v-model="showMenu"
      fixed
      clipped
      :disable-resize-watcher="true"
      temporary
    >
      <ac-nav-links
        v-model="showMenu"
        :subject-handler="subjectHandler"
        :is-staff="subject.is_staff"
        :is-superuser="subject.is_superuser"
        :is-logged-in="true"
        :is-registered="true"
        :embedded="true"
      />
    </v-navigation-drawer>
    <ac-form-dialog
      v-model="showNew"
      v-bind="newConversation.bind"
      title="Start a New Conversation"
      @submit="newConversation.submitThen(visitConversation)"
    >
      <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
        <v-row>
          <v-col cols="12" class="text-center">
            <span class="title">Quick check!</span>
          </v-col>
          <v-col cols="12">
            <ac-bound-field
              field-type="ac-captcha-field"
              :field="newConversation.fields.captcha"
              label="Prove you are human"
            />
          </v-col>
        </v-row>
      </v-col>
    </ac-form-dialog>
    <message-center
      v-if="powers.view_as && !isCurrent"
      :username="username"
      :model-value="showNotifications"
    />
  </v-toolbar>
</template>

<script setup lang="ts">
import AcConfirmation from "../../wrappers/AcConfirmation.vue"
import AcAvatar from "../../AcAvatar.vue"
import { useSubject } from "@/mixins/subjective.ts"
import AcNavLinks from "@/components/navigation/AcNavLinks.vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import { useEditable } from "@/mixins/editable.ts"
import AcFormDialog from "@/components/wrappers/AcFormDialog.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { SingleController } from "@/store/singles/controller.ts"
import {
  mdiLock,
  mdiPencil,
  mdiMenu,
  mdiMessage,
  mdiEyeOff,
  mdiEye,
  mdiCancel,
  mdiDotsHorizontal,
} from "@mdi/js"
import { useForm } from "@/store/forms/hooks.ts"
import { ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useViewer } from "@/mixins/viewer.ts"
import { profileLink } from "@/lib/otherFormatters.ts"
import { useDisplay } from "vuetify"
import type { Conversation, SubjectiveProps } from "@/types/main"
import { User } from "@/store/profiles/types/main"
import MessageCenter from "@/components/navigation/MessageCenter.vue"

const props = withDefaults(
  defineProps<SubjectiveProps & { dense?: boolean; showEdit?: boolean }>(),
  {
    dense: false,
    showEdit: false,
  },
)
const { rawViewerName, powers, isRegistered, viewer } = useViewer()
const { subject, subjectHandler, isCurrent, controls } = useSubject({ props })
const { editing } = useEditable(controls)
const router = useRouter()

const newConversation = useForm("new-conversation", {
  fields: {
    participants: { value: [] },
    captcha: { value: "" },
  },
  endpoint: `/api/profiles/account/${rawViewerName.value}/conversations/`,
})

const showNew = ref(false)
const showMenu = ref(false)
const display = useDisplay()
const showNotifications = ref(false)

const blockToggle = () => {
  ;(subjectHandler.user as SingleController<User>).patch({
    blocking: subject.value!.blocking,
  })
}

const visitConversation = (response: Conversation) => {
  router.push({
    name: "Conversation",
    params: {
      username: rawViewerName.value,
      conversationId: response.id + "",
    },
  })
}

const updateParticipants = () => {
  if (!subject.value) {
    return
  }
  const us = viewer.value as User
  if (!us || !us.id) {
    return
  }
  newConversation.fields.participants.model = [subject.value.id, us.id]
}

watch(subject, updateParticipants, { immediate: true })
watch(viewer, updateParticipants, { immediate: true })
</script>
