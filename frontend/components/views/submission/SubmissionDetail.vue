<template>
  <v-container fluid>
    <ac-load-section :controller="submission" fluid>
      <template v-slot:default>
        <v-layout row wrap>
          <v-flex xs12 md9 lg9 xl10>
            <ac-asset :asset="submission.x" thumb-name="gallery" aspect-ratio="" :contain="true" :editing="editing" v-model="showEditAsset">
              <template slot="edit-menu">
                <ac-expanded-property v-model="showEditAsset">
                  <v-tabs v-model="editAssetTab">
                    <v-tab>Edit File</v-tab>
                    <v-tab>Preview Listing</v-tab>
                  </v-tabs>
                  <v-tabs-items v-model="editAssetTab" class="pt-2">
                    <v-tab-item>
                      <ac-patch-field
                          field-type="ac-uppy-file"
                          :patcher="submission.patchers.file"
                          label="Upload a file for this submission"
                      ></ac-patch-field>
                    </v-tab-item>
                    <v-tab-item>
                      <v-layout row wrap>
                        <v-flex xs12 sm6 d-flex>
                          <v-layout row justify-content align-center>
                            <v-flex>
                              <ac-patch-field
                                  field-type="ac-uppy-file"
                                  :patcher="submission.patchers.preview"
                                  label="Preview Image"
                                  :show-reset="false" :show-clear="true"
                              ></ac-patch-field>
                            </v-flex>
                          </v-layout>
                        </v-flex>
                        <v-flex xs12 sm6>
                          <ac-gallery-preview :submission="submission.x"></ac-gallery-preview>
                        </v-flex>
                      </v-layout>
                    </v-tab-item>
                  </v-tabs-items>
                </ac-expanded-property>
              </template>
            </ac-asset>
          </v-flex>
          <v-flex xs12 md3 lg3 xl2 class="px-2">
            <v-layout column>
              <v-flex>
                <v-layout row wrap>
                  <v-flex xs5 sm3 md12 lg5>
                    <v-btn block @click="submission.patch({favorites: !submission.x.favorites})"
                           color="secondary">
                      <v-icon left v-if="favorite">favorite</v-icon>
                      <v-icon left v-else>favorite_border</v-icon>
                      Fav
                    </v-btn>
                  </v-flex>
                  <v-flex xs7 sm4 lg7 md12>
                    <v-btn color="primary" block :href="submission.x.file.full" download>
                      <v-icon left>save_alt</v-icon>
                      Download
                    </v-btn>
                  </v-flex>
                  <v-flex xs12 sm5 md12 v-if="submission.x.commission_link">
                    <v-btn color="green" block :to="submission.x.commission_link">
                      <v-icon left>palette</v-icon>
                      Commission the artist!
                    </v-btn>
                  </v-flex>
                  <v-flex xs12>
                    <ac-share-button block :title="windowTitle">
                      <span slot="title">Share {{submission.x.title}}</span>
                      <template v-slot:footer v-if="controls">
                        <ac-load-section :controller="sharedWith">
                          <ac-share-manager :controller="sharedWith"></ac-share-manager>
                        </ac-load-section>
                      </template>
                    </ac-share-button>
                  </v-flex>
                </v-layout>
              </v-flex>
              <v-flex>
                <ac-tag-display :patcher="submission.patchers.tags"
                                :editable="submission.x.owner.taggable"
                                :username="submission.x.owner.username"
                                scope="Submissions"
                ></ac-tag-display>
              </v-flex>
              <v-flex>
                <ac-artist-display :controller="artists" :submission-id="submissionId"
                                   :editable="submission.x.owner.taggable"
                                   :controls="tagControls"></ac-artist-display>
              </v-flex>
              <v-flex>
                <ac-character-display :controller="characters" :submission-id="submissionId"
                                      :editable="submission.x.owner.taggable"
                                      :controls="tagControls"></ac-character-display>
              </v-flex>
              <v-flex class="pt-2">
                <h3>You might also like...</h3>
                <v-layout row wrap>
                  <v-flex xs4 sm2 lg6 xl4 v-for="submission in recommended.list" :key="submission.id">
                    <ac-gallery-preview
                        :submission="submission.x"
                        :show-footer="false"
                    ></ac-gallery-preview>
                  </v-flex>
                </v-layout>
              </v-flex>
            </v-layout>
          </v-flex>
          <v-container class="pt-3">
            <v-card>
              <v-card :color="$vuetify.theme.darkBase.darken4" class="px-3">
                <v-layout row>
                  <v-flex d-flex>
                    <v-layout row justify-content align-center>
                      <v-flex>
                        <v-toolbar-title v-show="!editing" class="wrap">{{submission.x.title}}
                        </v-toolbar-title>
                        <ac-patch-field label="Title" :patcher="submission.patchers.title"
                                        v-if="controls" v-show="editing"></ac-patch-field>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                  <v-spacer></v-spacer>
                  <v-flex shrink hidden-xs-only :class="{'d-flex': $vuetify.breakpoint.smAndUp}">
                    <v-layout row justify-content align-center>
                      <v-flex>
                        <ac-avatar :user="submission.x.owner" :show-name="false"></ac-avatar>
                      </v-flex>
                      <v-flex class="px-2">
                        <v-toolbar-title>{{submission.x.owner.username}}</v-toolbar-title>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                  <v-flex shrink d-flex>
                    <v-layout row align-center justify-content>
                      <v-flex>
                        <v-menu offset-x left v-if="controls">
                          <template v-slot:activator="{on}">
                            <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
                          </template>
                          <v-list dense>
                            <v-list-tile @click.stop="submission.patch({private: !submission.x.private})">
                              <v-list-tile-action>
                                <v-icon v-if="submission.x.private">visibility_off</v-icon>
                                <v-icon v-else>visibility</v-icon>
                              </v-list-tile-action>
                              <v-list-tile-title>
                                <span v-if="submission.x.private">Hidden</span>
                                <span v-else>Public</span>
                              </v-list-tile-title>
                            </v-list-tile>
                            <v-list-tile @click.stop="submission.patch({comments_disabled: !submission.x.comments_disabled})" v-if="controls">
                              <v-list-tile-action>
                                <v-icon v-if="submission.x.comments_disabled">mode_comment</v-icon>
                                <v-icon v-else>comment</v-icon>
                              </v-list-tile-action>
                              <v-list-tile-title>
                                Comments
                                <span v-if="submission.x.comments_disabled">locked</span>
                                <span v-else>allowed</span>
                              </v-list-tile-title>
                            </v-list-tile>
                            <ac-confirmation :action="deleteSubmission">
                              <template v-slot:default="confirmContext">
                                <v-list-tile v-on="confirmContext.on">
                                  <v-list-tile-action class="delete-button"><v-icon>delete</v-icon></v-list-tile-action>
                                  <v-list-tile-title>Delete</v-list-tile-title>
                                </v-list-tile>
                              </template>
                            </ac-confirmation>
                          </v-list>
                        </v-menu>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                </v-layout>
              </v-card>
              <v-card-text>
                <v-layout row wrap>
                  <v-flex xs12 md8 xl9>
                    <ac-rendered :value="submission.x.caption" v-show="!editing"></ac-rendered>
                    <ac-patch-field
                        field-type="ac-editor"
                        :auto-save="false"
                        :patcher="submission.patchers.caption"
                        v-if="controls"
                        v-show="editing"
                        label="Description"
                        hint="Describe this piece-- how it came to be, how it makes you feel, or give it a caption."
                        :save-comparison="submission.x.caption"/>
                  </v-flex>
                  <v-flex xs12 md3 xl2 offset-md1>
                    <v-layout row wrap>
                      <v-flex xs12>
                        <h3>Info</h3>
                        <v-divider></v-divider>
                      </v-flex>
                      <v-flex xs4 hidden-sm-and-up :class="{'d-flex': $vuetify.breakpoint.xs}">
                        <v-layout justify-content align-center>
                          <strong>Submitted by:</strong>
                        </v-layout>
                      </v-flex>
                      <v-flex xs8 pt-2 hidden-sm-and-up>
                        <ac-avatar :user="submission.x.owner"></ac-avatar>
                      </v-flex>
                      <v-flex xs4><strong>Views:</strong></v-flex>
                      <v-flex xs8 text-xs-center>{{submission.x.hits}}</v-flex>
                      <v-flex xs4><strong>Created on:</strong></v-flex>
                      <v-flex xs8 text-xs-center>{{formatDateTime(submission.x.created_on)}}</v-flex>
                      <v-flex xs4><strong>Favorites:</strong></v-flex>
                      <v-flex xs8 text-xs-center>{{submission.x.favorite_count}}</v-flex>
                      <v-flex xs4 v-if="submission.x.order && controls"><strong>From Order:</strong></v-flex>
                      <v-flex xs8 text-xs-center v-if="submission.x.order && controls">
                        <router-link :to="{name: 'Order', params: {username: submission.x.owner.username, orderId: submission.x.order}}">
                          {{submission.x.order}}
                        </router-link>
                      </v-flex>
                      <v-flex xs12 text-xs-center>
                        <v-btn class="mx-0 rating-button" small :color="ratingColor[submission.x.rating]" @click="showRating" :ripple="editing">
                          <v-icon left v-if="editing">edit</v-icon>
                          {{ratingsShort[submission.x.rating]}}
                        </v-btn>
                        <ac-expanded-property v-model="ratingDialog">
                          <ac-patch-field field-type="ac-rating-field" :patcher="submission.patchers.rating"></ac-patch-field>
                        </ac-expanded-property>
                      </v-flex>
                    </v-layout>
                  </v-flex>
                </v-layout>
              </v-card-text>
            </v-card>
          </v-container>
          <v-flex xs12>
            <ac-comment-section :commentList="comments" :nesting="true" :locked="locked"></ac-comment-section>
          </v-flex>
        </v-layout>
        <ac-editing-toggle v-if="controls"></ac-editing-toggle>
      </template>
    </ac-load-section>
  </v-container>
</template>

<style>
  .wrap {
    white-space: normal;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {SingleController} from '@/store/singles/controller'
import Submission from '@/types/Submission'
import {Prop, Watch} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import Formatting from '@/mixins/formatting'
import {ListController} from '@/store/lists/controller'
import {Journal} from '@/types/Journal'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {posse, RATING_COLOR, RATINGS_SHORT, setMetaContent, textualize, updateTitle} from '@/lib'
import AcAvatar from '@/components/AcAvatar.vue'
import Editable from '@/mixins/editable'
import AcEditingToggle from '@/components/navigation/AcEditingToggle.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRelatedManager from '@/components/wrappers/AcRelatedManager.vue'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {FormController} from '@/store/forms/form-controller'
import AcArtistDisplay from './AcArtistDisplay.vue'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import {Character} from '@/store/characters/types/Character'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcShareButton from '@/components/AcShareButton.vue'
import AcShareManager from '@/components/AcShareManager.vue'

  @Component({
    components: {
      AcShareManager,
      AcShareButton,
      AcGalleryPreview,
      AcFormContainer,
      AcBoundField,
      AcFormDialog,
      AcConfirmation,
      AcExpandedProperty,
      AcCharacterDisplay,
      AcArtistDisplay,
      AcRelatedManager,
      AcPatchField,
      AcRendered,
      AcEditingToggle,
      AcAvatar,
      AcCommentSection,
      AcTagDisplay,
      AcAsset,
      AcLoadSection,
    },
  })
export default class SubmissionDetail extends mixins(Viewer, Formatting, Editable) {
    @Prop({required: true})
    public submissionId!: number
    public submission: SingleController<Submission> = null as unknown as SingleController<Submission>
    public comments: ListController<Journal> = null as unknown as ListController<Journal>
    public artists: ListController<TerseUser> = null as unknown as ListController<TerseUser>
    public sharedWith: ListController<TerseUser> = null as unknown as ListController<TerseUser>
    public characters: ListController<Character> = null as unknown as ListController<Character>
    public recommended: ListController<Submission> = null as unknown as ListController<Submission>
    public editAsset: FormController = null as unknown as FormController
    public ratingsShort = RATINGS_SHORT
    public ratingColor = RATING_COLOR
    public ratingDialog = false
    public showEditAsset = false
    public editAssetTab = 0

    public get url() {
      return `/api/profiles/v1/submission/${this.submissionId}/`
    }

    public get favorite() {
      return this.submission.x && this.submission.x.favorites
    }

    public get controls() {
      // istanbul ignore if
      if (!this.submission.x) {
        return false
      }
      return this.isStaff || (this.submission.x.owner.username === this.rawViewerName)
    }

    public get windowTitle() {
      // istanbul ignore if
      if (!this.submission.x) {
        return ''
      }
      let title = this.submission.x.title
      if (title) {
        title += ' -- '
      }
      if (this.artists.list.length) {
        if (title) {
          title += 'by '
        } else {
          title += 'By '
        }
        // @ts-ignore
        const artistNames = this.artists.list.map((user) => (user.x.user as TerseUser).username)
        const firstNames = artistNames.slice(0, 4)
        title += posse(firstNames, artistNames.length - firstNames.length)
      } else {
        title += `Submitted by ${this.submission.x.owner.username}`
      }
      title += ' - (Artconomy.com)'
      return title
    }

    public get tagControls() {
      const submission = this.submission.x as Submission
      return this.controls || submission.owner.taggable
    }

    public get locked() {
      return !(this.submission.x) || this.submission.x.comments_disabled
    }

    public setMeta(submission: Submission|null|false) {
      if (!submission) {
        return
      }
      updateTitle(this.windowTitle)
      setMetaContent('description', textualize(submission.caption).slice(0, 160))
    }

    @Watch('submission.x')
    public submissionMeta(submission: Submission|null) {
      this.setMeta(submission)
    }

    @Watch('submission.x')
    public artistMeta(submission: Submission|null) {
      this.setMeta(this.submission.x)
    }

    public showRating() {
      if (this.editing) {
        this.ratingDialog = true
      }
    }

    public deleteSubmission() {
      const submission = this.submission.x as Submission
      this.submission.delete().then(() => {
        this.$router.replace({name: 'Profile', params: {username: submission.owner.username}})
      })
    }

    public created() {
      this.submission = this.$getSingle(
        `submission__${this.submissionId}`, {endpoint: this.url, params: {view: 'true'}}
      )
      this.artists = this.$getList(`submission__${this.submissionId}__artists`, {
        endpoint: `${this.url}artists/`, paginated: false,
      })
      this.characters = this.$getList(`submission__${this.submissionId}__characters`, {
        endpoint: `${this.url}characters/`,
        paginated: false,
      })
      this.sharedWith = this.$getList(`submission__${this.submissionId}__share`, {
        endpoint: `${this.url}share/`,
        paginated: false,
      })
      this.comments = this.$getList(
        `submission-${this.submissionId}-comments`, {
          endpoint: `/api/lib/v1/comments/profiles.Submission/${this.submissionId}/`,
          reverse: true,
          grow: true,
          pageSize: 5,
        })
      this.recommended = this.$getList(
        `submission-${this.submissionId}-recommended`, {
          endpoint: `${this.url}recommended/`,
          pageSize: 6,
        })
      this.editAsset = this.$getForm(
        `submission__${this.submissionId}`, {
          endpoint: this.url,
          fields: {file: {value: ''}, preview: {value: ''}},
          method: 'patch',
        }
      )
      this.submission.get().catch(this.setError)
      this.artists.firstRun()
      this.characters.firstRun()
      this.sharedWith.firstRun().catch(this.statusOk(403))
      this.recommended.firstRun()
    }
}
</script>
