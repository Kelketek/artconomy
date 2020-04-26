<template>
  <v-toolbar :dense="dense" color="black">
    <ac-avatar :username="username" :show-name="false" />
    <v-toolbar-title class="ml-1"><ac-link :to="subject && profileLink(subject)">{{subjectHandler.displayName}}</ac-link></v-toolbar-title>
    <v-spacer />
    <v-toolbar-items v-if="subject && showActions && $vuetify.breakpoint.smAndUp">
      <v-btn color="secondary" @click="showMenu=true" v-if="isStaff">
        <v-icon left>menu</v-icon> Menu
      </v-btn>
      <v-btn color="primary" class="message-button" @click="startConversation">
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
        <v-list-item class="message-button" @click="startConversation">
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
import {artCall, profileLink} from '@/lib/lib'
import {Conversation} from '@/types/Conversation'
import {User} from '@/store/profiles/types/User'
import {Prop} from 'vue-property-decorator'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import Editable from '@/mixins/editable'

  @Component({
    components: {AcLink, AcExpandedProperty, AcNavLinks, AcAvatar, AcConfirmation},
  })
export default class AcProfileHeader extends mixins(Subjective, Formatting, Editable) {
    @Prop({default: false})
    public dense!: boolean
    @Prop({default: false})
    public showEdit!: boolean
    public showMenu = false
    public get showActions() {
      return !this.isCurrent && this.isRegistered
    }
    public startConversation() {
      artCall({
        url: `/api/profiles/v1/account/${this.viewerName}/conversations/`,
        method: 'post',
        data: {participants: [(this.subject as User).id]},
      }).then(this.visitConversation)
    }

    public visitConversation(response: Conversation) {
      this.$router.push({name: 'Conversation', params: {username: this.rawViewerName, conversationId: response.id + ''}})
    }
}
</script>
