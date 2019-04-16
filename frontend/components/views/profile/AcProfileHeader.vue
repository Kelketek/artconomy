<template>
  <v-toolbar :dense="dense">
    <ac-avatar :username="username" :show-name="false"></ac-avatar>
    <v-toolbar-title>{{subjectHandler.displayName}}</v-toolbar-title>
    <v-spacer></v-spacer>
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
        <v-flex slot="confirmation-text">
          <v-flex v-if="subject.blocking">
            <p>
              Are you sure you wish to unblock {{subjectHandler.displayName}}? They will be able to message you, comment, and
              perform other interactive actions with your account.
            </p>
          </v-flex>
          <v-flex v-else>
            <p>
              Are you sure you wish to block {{subjectHandler.displayName}}? They will not be able to message you, comment on your
              items, or perform other interactive actions with your account.
            </p>
            <p v-if="subject.watching">This will also remove them from your watchlist.</p>
          </v-flex>
        </v-flex>
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
        <v-list-tile v-if="isStaff" @click="showMenu=true">
          <v-list-tile-action>
            <v-icon>menu</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>Menu</v-list-tile-title>
        </v-list-tile>
        <v-list-tile class="message-button" @click="startConversation">
          <v-list-tile-action><v-icon>message</v-icon></v-list-tile-action>
          <v-list-tile-title>Message</v-list-tile-title>
        </v-list-tile>
        <v-list-tile @click="subjectHandler.user.patch({watching: !subject.watching})">
          <v-list-tile-action>
            <v-icon v-if="subject.watching">visibility_off</v-icon>
            <v-icon v-else>visibility</v-icon>
          </v-list-tile-action>
          <v-list-tile-title>
            <span v-if="subject.watching">Unwatch</span>
            <span v-else>Watch</span>
          </v-list-tile-title>
        </v-list-tile>
        <ac-confirmation :action="() => {subjectHandler.user.patch({blocking: !subject.blocking})}">
          <v-flex slot="confirmation-text">
            <v-flex v-if="subject.blocking">
              <p>
                Are you sure you wish to unblock {{subjectHandler.displayName}}? They will be able to message you, comment, and
                perform other interactive actions with your account.
              </p>
            </v-flex>
            <v-flex v-else>
              <p>
                Are you sure you wish to block {{subjectHandler.displayName}}? They will not be able to message you, comment on your
                items, or perform other interactive actions with your account.
              </p>
              <p v-if="subject.watching">This will also remove them from your watchlist.</p>
            </v-flex>
          </v-flex>
          <template v-slot:default="{on}">
            <v-list-tile v-on="on">
              <v-list-tile-action>
                <v-icon>block</v-icon>
              </v-list-tile-action>
              <v-list-tile-title>
                <span v-if="subject.blocking">Unblock</span>
                <span v-if="!subject.blocking">Block</span>
              </v-list-tile-title>
            </v-list-tile>
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
  </v-toolbar>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcConfirmation from '../../wrappers/AcConfirmation.vue'
import AcAvatar from '../../AcAvatar.vue'
import Subjective from '@/mixins/subjective'
import {artCall} from '@/lib'
import {Conversation} from '@/types/Conversation'
import {User} from '@/store/profiles/types/User'
import {Prop} from 'vue-property-decorator'
import AcNavLinks from '@/components/navigation/AcNavLinks.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'

  @Component({
    components: {AcExpandedProperty, AcNavLinks, AcAvatar, AcConfirmation},
  })
export default class AcProfileHeader extends mixins(Subjective) {
    @Prop({default: false})
    public dense!: boolean
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
