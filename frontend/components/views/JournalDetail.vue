<template>
  <ac-load-section :controller="journal">
    <template v-slot:default>
      <v-container v-if="journal.x">
        <v-row>
          <v-col>
            <v-card>
              <v-toolbar dense color="black">
                <ac-avatar :username="username" :show-name="false" class="ml-3"/>
                <v-toolbar-title class="ml-1">
                  <ac-link :to="profileLink(subject)">{{username}}</ac-link>
                </v-toolbar-title>
                <v-spacer/>
                <v-tooltip bottom>
                  <template v-slot:activator="{props}">
                    <v-icon v-bind="props" icon="mdi-information"/>
                  </template>
                  {{formatDateTime(journal.x.created_on)}}
                  <span v-if="journal.x.edited"><br/>Edited: {{formatDateTime(journal.x.edited_on)}}</span>
                </v-tooltip>
                <v-menu offset-x left :close-on-content-click="false" :attach="$menuTarget">
                  <template v-slot:activator="{props}">
                    <v-btn icon v-bind="props" class="more-button">
                      <v-icon icon="mdi-dots-horizontal"/>
                    </v-btn>
                  </template>
                  <v-list dense>
                    <v-list-item @click.stop="editing = !editing" class="edit-toggle">
                      <template v-slot:prepend>
                        <v-icon v-if="editing" icon="mdi-lock"/>
                        <v-icon v-else icon="mdi-pencil"/>
                      </template>
                      <v-list-item-title v-if="editing">Lock</v-list-item-title>
                      <v-list-item-title v-else>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click.stop="journal.patch({subscribed: !journal.x.subscribed})">
                      <template v-slot:prepend>
                        <v-icon v-if="journal.x.subscribed" icon="mdi-volume-high"/>
                        <v-icon v-else icon="mdi-volume-off"/>
                      </template>
                      <v-list-item-title>
                        Notifications
                        <span v-if="journal.x.subscribed">on</span>
                        <span v-else>off</span>
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item
                        @click="journal.patchers.comments_disabled.model = !journal.patchers.comments_disabled.model">
                      <template v-slot:prepend>
                        <v-switch :model-value="journal.patchers.comments_disabled.model" color="primary"
                                  :hide-details="true"/>
                      </template>
                      <v-list-item-title>
                        Comments Disabled
                      </v-list-item-title>
                    </v-list-item>
                    <ac-confirmation :action="deleteJournal" v-if="controls">
                      <template v-slot:default="confirmContext">
                        <v-list-item v-on="confirmContext.on">
                          <template v-slot:prepend>
                            <v-icon class="delete-button" icon="mdi-delete"/>
                          </template>
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
                    <ac-patch-field :patcher="journal.patchers.subject" v-show="editing" v-if="controls"/>
                    <h1 class="text-h5" v-show="!editing"><ac-rendered :value="journal.x.subject"
                                                                       :inline="true"/></h1>
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field field-type="ac-editor" v-show="editing" v-if="controls" :patcher="journal.patchers.body"
                                    :auto-save="false">
                      <template v-slot:pre-actions>
                        <v-col class="shrink">
                          <v-tooltip top>
                            <template v-slot:activator="{ props }">
                              <v-btn v-bind="props" @click="editing=false" icon color="danger" class="cancel-button">
                                <v-icon icon="mdi-lock"/>
                              </v-btn>
                            </template>
                            <span>Stop Editing</span>
                          </v-tooltip>
                        </v-col>
                      </template>
                    </ac-patch-field>
                    <ac-rendered :value="journal.x.body" v-show="!editing"/>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <ac-comment-section :commentList="journalComments" :nesting="true" :locked="locked"/>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>
<script lang="ts">
import Editable from '@/mixins/editable'
import AcAvatar from '@/components/AcAvatar.vue'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller'
import Subjective from '@/mixins/subjective'
import {Patch} from '@/store/singles/patcher'
import {Journal} from '@/types/Journal'
import AcRendered from '@/components/wrappers/AcRendered'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {ListController} from '@/store/lists/controller'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Formatting from '@/mixins/formatting'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({
  components: {
    AcLoadSection,
    AcLink,
    AcPatchField,
    AcCommentSection,
    AcConfirmation,
    AcLoadingSpinner,
    AcEditor,
    AcRendered,
    AcAvatar,
  },
})
class JournalDetail extends mixins(Subjective, Editable, Formatting) {
  @Prop({required: true})
  public journalId!: number

  public journal = null as unknown as SingleController<Journal>
  public journalComments = null as unknown as ListController<Journal>

  public created() {
    this.journal = this.$getSingle(
        `journal-${this.journalId}`, {
          endpoint: `/api/profiles/account/${this.username}/journals/${this.journalId}/`,
        })
    this.journal.get().catch(this.setError)
    this.journalComments = this.$getList(
        `journal-${this.journalId}-comments`, {
          endpoint: `/api/lib/comments/profiles.Journal/${this.journalId}/`,
          reverse: true,
          grow: true,
          params: {size: 5},
        })
    this.journalComments.firstRun()
  }

  public async deleteJournal() {
    return this.journal.delete().then(this.goBack)
  }

  public get locked() {
    return !this.journal.x || this.journal.x!.comments_disabled
  }

  public goBack() {
    this.$router.push({
      name: 'Profile',
      params: {username: this.username},
    })
  }
}

export default toNative(JournalDetail)
</script>
