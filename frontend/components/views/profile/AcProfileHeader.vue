<template>
  <v-toolbar :dense="dense" color="black">
    <ac-avatar :username="username" :show-name="false" />
    <v-toolbar-title class="ml-1"><ac-link :to="subject && profileLink(subject)">{{subjectHandler.displayName}}</ac-link></v-toolbar-title>
    <v-spacer />
    <v-toolbar-items v-if="subject && showActions && $vuetify.breakpoint.smAndUp">
      <v-btn color="secondary" @click="showMenu=true" v-if="isStaff">
        <v-icon left>menu</v-icon> Menu
      </v-btn>
      <v-btn color="primary" class="message-button" @click="showNew = true">
        <v-icon left>message</v-icon> Message
      </v-btn>
      <v-btn color="grey darken-2" @click="subjectHandler.user.patch({watching: !subject.watching})">
        <v-icon left v-if="subject.watching">visibility_off</v-icon>
        <v-icon left v-else>visibility</v-icon>
        <span v-if="subject.watching">Unwatch</span>
        <span v-else>Watch</span>
      </v-btn>
      <!--suppress JSCheckFunctionSignatures -->
      <ac-confirmation :action="() => {subjectHandler.user.patch({blocking: !subject.blocking})}">
        <v-col slot="confirmation-text">
          <v-col v-if="subject.blocking">
            <p>
              Are you sure you wish to unblock {{subjectHandler.displayName}}? They will be able to message you, comment, and
              perform other interactive actions with your account.
            </p>
          </v-col>
          <v-col v-else>
            <p>
              Are you sure you wish to block {{subjectHandler.displayName}}? They will not be able to message you, comment on your
              items, or perform other interactive actions with your account.
            </p>
            <p v-if="subject.watching">This will also remove them from your watchlist.</p>
          </v-col>
        </v-col>
        <template v-slot:default="{on}">
          <v-btn color="red" v-on="on">
            <v-icon left>block</v-icon>
            <span v-if="subject.blocking">Unblock</span>
            <span v-else>Block</span>
          </v-btn>
        </template>
      </ac-confirmation>
      <ac-form-dialog
          v-model="showNew"
          v-bind="newConversation.bind"
          @submit="newConversation.submitThen(visitConversation)"
          title="Start a New Conversation"
      >
        <v-col cols="12" sm="10" offset-sm="1" offset-md="2" md="8">
          <v-row>
            <v-col cols="12" class="text-center">
              <span class="title">Quick check!</span>
            </v-col>
            <v-col cols="12">
              <ac-bound-field
                  field-type="ac-captcha-field" :field="newConversation.fields.captcha" label="Prove you are human"
              />
            </v-col>
          </v-row>
        </v-col>
      </ac-form-dialog>
    </v-toolbar-items>
    <v-menu offset-y v-else-if="subject && showActions">
      <template v-slot:activator="{on}">
        <v-btn v-on="on" icon>
          <v-icon>more_horiz</v-icon>
        </v-btn>
      </template>
      <v-list dense>
        <v-list-item v-if="isStaff" @click="showMenu=true">
          <v-list-item-action>
            <v-icon>menu</v-icon>
          </v-list-item-action>
          <v-list-item-title>Menu</v-list-item-title>
        </v-list-item>
        <v-list-item class="message-button" @click="showNew = true">
          <v-list-item-action><v-icon>message</v-icon></v-list-item-action>
          <v-list-item-title>Message</v-list-item-title>
        </v-list-item>
        <v-list-item @click="subjectHandler.user.patch({watching: !subject.watching})">
          <v-list-item-action>
            <v-icon v-if="subject.watching">visibility_off</v-icon>
            <v-icon v-else>visibility</v-icon>
          </v-list-item-action>
          <v-list-item-title>
            <span v-if="subject.watching">Unwatch</span>
            <span v-else>Watch</span>
          </v-list-item-title>
        </v-list-item>
        <ac-confirmation :action="() => {subjectHandler.user.patch({blocking: !subject.blocking})}">
          <v-col slot="confirmation-text">
            <v-col v-if="subject.blocking">
              <p>
                Are you sure you wish to unblock {{subjectHandler.displayName}}? They will be able to message you, comment, and
                perform other interactive actions with your account.
              </p>
            </v-col>
            <v-col v-else>
              <p>
                Are you sure you wish to block {{subjectHandler.displayName}}? They will not be able to message you, comment on your
                items, or perform other interactive actions with your account.
              </p>
              <p v-if="subject.watching">This will also remove them from your watchlist.</p>
            </v-col>
          </v-col>
          <template v-slot:default="{on}">
            <v-list-item v-on="on">
              <v-list-item-action>
                <v-icon>block</v-icon>
              </v-list-item-action>
              <v-list-item-title>
                <span v-if="subject.blocking">Unblock</span>
                <span v-if="!subject.blocking">Block</span>
              </v-list-item-title>
            </v-list-item>
          </template>
        </ac-confirmation>
      </v-list>
    </v-menu>
    <v-dialog v-model="showMenu">
      <v-navigation-drawer v-model="showMenu" v-if="isStaff && subject" fixed clipped :disable-resize-watcher="true">
        <ac-nav-links
            :subject-handler="subjectHandler"
            :is-staff="subject.is_staff"
            :is-superuser="subject.is_superuser"
            :is-logged-in="true"
            :is-registered="true"
            :embedded="true"
            v-model="showMenu"
        />
      </v-navigation-drawer>
    </v-dialog>
    <v-menu offset-x left v-if="controls && showEdit">
      <template v-slot:activator="{on}">
        <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
      </template>
      <v-list dense>
        <v-list-item @click.stop="editing = !editing" v-if="showEdit">
          <v-list-item-action>
            <v-icon v-if="editing">lock</v-icon>
            <v-icon v-else>edit</v-icon>
          </v-list-item-action>
          <v-list-item-title v-if="editing">Lock</v-list-item-title>
          <v-list-item-title v-else>Edit</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-toolbar>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcConfirmation from '../../wrappers/AcConfirmation.vue'
import AcAvatar from '../../AcAvatar.vue'
import Subjective from '@/mixins/subjective'
import {Conversation} from '@/types/Conversation'
import {User} from '@/store/profiles/types/User'
import {Prop, Watch} from 'vue-property-decorator'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import Editable from '@/mixins/editable'
import {FormController} from '@/store/forms/form-controller'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField'

  @Component({
    components: {
      AcBoundField,
      AcFormDialog,
      AcLink,
      AcExpandedProperty,
      AcNavLinks,
      AcAvatar,
      AcConfirmation,
    },
  })
export default class AcProfileHeader extends mixins(Subjective, Formatting, Editable) {
    @Prop({default: false})
    public dense!: boolean

    @Prop({default: false})
    public showEdit!: boolean

    public showNew = false

    public newConversation = null as unknown as FormController

    public showMenu = false
    public get showActions() {
      return !this.isCurrent && this.isRegistered
    }

    public visitConversation(response: Conversation) {
      this.$router.push({name: 'Conversation', params: {username: this.rawViewerName, conversationId: response.id + ''}})
    }

    @Watch('subject')
    public populateRecepient(value: User) {
      if (!value) {
        return
      }
      this.newConversation.fields.participants.model = [value.id]
    }

    public created() {
      this.newConversation = this.$getForm('new-conversation', {
        fields: {participants: {value: []}, captcha: {value: ''}},
        endpoint: `/api/profiles/v1/account/${this.rawViewerName}/conversations/`,
      })
    }
}
</script>
