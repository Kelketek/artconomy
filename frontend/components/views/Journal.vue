<template>
  <ac-load-section :controller="journal">
    <template v-slot:default>
      <v-container>
        <v-row>
          <v-col>
            <v-card>
              <v-toolbar dense color="black">
                <ac-avatar :username="username" :show-name="false" />
                <v-toolbar-title class="ml-1"><ac-link :to="profileLink(subject)">{{username}}</ac-link></v-toolbar-title><v-spacer />
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }">
                    <v-icon v-on="on">info</v-icon>
                  </template>
                  {{formatDateTime(journal.x.created_on)}}
                  <span v-if="journal.x.edited"><br/>Edited: {{formatDateTime(journal.x.edited_on)}}</span>
                </v-tooltip>
                <v-menu offset-x left>
                  <template v-slot:activator="{on}">
                    <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
                  </template>
                  <v-list dense>
                    <v-list-item @click.stop="editing = !editing">
                      <v-list-item-action>
                        <v-icon v-if="editing">lock</v-icon>
                        <v-icon v-else>edit</v-icon>
                      </v-list-item-action>
                      <v-list-item-title v-if="editing">Lock</v-list-item-title>
                      <v-list-item-title v-else>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click.stop="journal.patch({subscribed: !journal.x.subscribed})">
                      <v-list-item-action>
                        <v-icon v-if="journal.x.subscribed">volume_up</v-icon>
                        <v-icon v-else>volume_off</v-icon>
                      </v-list-item-action>
                      <v-list-item-title>
                        Notifications
                        <span v-if="journal.x.subscribed">on</span>
                        <span v-else>off</span>
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item @click.stop="journal.patch({comments_disabled: !journal.x.comments_disabled})">
                      <v-list-item-action>
                        <v-icon v-if="journal.x.comments_disabled">mode_comment</v-icon>
                        <v-icon v-else>comment</v-icon>
                      </v-list-item-action>
                      <v-list-item-title>
                        Comments
                        <span v-if="journal.x.comments_disabled">locked</span>
                        <span v-else>allowed</span>
                      </v-list-item-title>
                    </v-list-item>
                    <ac-confirmation :action="deleteJournal" v-if="controls">
                      <template v-slot:default="confirmContext">
                        <v-list-item v-on="confirmContext.on">
                          <v-list-item-action class="delete-button"><v-icon>delete</v-icon></v-list-item-action>
                          <v-list-item-title>Delete</v-list-item-title>
                        </v-list-item>
                      </template>
                    </ac-confirmation>
                  </v-list>
                </v-menu>
              </v-toolbar>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
                    <ac-patch-field :patcher="journalSubject" v-show="editing" v-if="controls" />
                    <span class="title" v-show="!editing"><ac-rendered :value="journal.x.subject" :inline="true" /></span>
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field field-type="ac-editor" v-show="editing" v-if="controls" :patcher="body" :auto-save="false">
                      <v-col class="shrink" slot="pre-actions">
                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-btn v-on="on" @click="editing=false" icon color="danger" class="cancel-button" :disabled="journal.patching">
                              <v-icon>lock</v-icon>
                            </v-btn>
                          </template>
                          <span>Stop Editing</span>
                        </v-tooltip>
                      </v-col>
                    </ac-patch-field>
                    <ac-rendered :value="journal.x.body" v-show="!editing" />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
            <ac-editing-toggle v-if="controls" />
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <ac-comment-section :commentList="journalComments" :nesting="true" :locked="locked" />
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>
<script lang="ts">
import Editable from '@/mixins/editable'
import AcAvatar from '@/components/AcAvatar.vue'
import Component, {mixins} from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import {Journal} from '@/types/Journal'
import Subjective from '@/mixins/subjective'
import {Prop} from 'vue-property-decorator'
import {Patch} from '@/store/singles/patcher'
import AcRendered from '@/components/wrappers/AcRendered'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcSpeedButton from '@/components/wrappers/AcSpeedButton.vue'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {ListController} from '@/store/lists/controller'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Formatting from '@/mixins/formatting'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({components: {
  AcLoadSection,
  AcLink,
  AcPatchField,
  AcCommentSection,
  AcConfirmation,
  AcEditingToggle,
  AcSpeedButton,
  AcLoadingSpinner,
  AcEditor,
  AcRendered,
  AcAvatar}})
export default class extends mixins(Subjective, Editable, Formatting) {
    @Prop({required: true})
    public journalId!: number

    public journal: SingleController<Journal> = null as unknown as SingleController<Journal>
    public body: Patch = null as unknown as Patch
    public journalComments: ListController<Journal> = null as unknown as ListController<Journal>
    public journalSubject: Patch = null as unknown as Patch
    public commentsDisabled: Patch = null as unknown as Patch

    public created() {
      this.body = this.$makePatcher({modelProp: 'journal', attrName: 'body'})
      this.journal = this.$getSingle(
        `journal-${this.journalId}`, {
          endpoint: `/api/profiles/v1/account/${this.username}/journals/${this.journalId}/`,
        })
      this.journal.get().catch(this.setError)
      this.journalComments = this.$getList(
        `journal-${this.journalId}-comments`, {
          endpoint: `/api/lib/v1/comments/profiles.Journal/${this.journalId}/`,
          reverse: true,
          grow: true,
          pageSize: 5,
        })
      this.journalComments.firstRun()
      this.journalSubject = this.$makePatcher(
        {modelProp: 'journal', attrName: 'subject', debounceRate: 300, refresh: false})
      this.commentsDisabled = this.$makePatcher(
        {modelProp: 'journal', attrName: 'comments_disabled'})
    }
    public deleteJournal() {
      return this.journal.delete().then(this.goBack)
    }

    public get locked() {
      return !(this.journal.x) || this.journal.x.comments_disabled
    }
    public goBack() {
      this.$router.push({name: 'Profile', params: {username: this.username}})
    }
}
</script>
