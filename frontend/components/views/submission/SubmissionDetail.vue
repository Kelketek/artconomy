<template>
  <v-container fluid>
    <ac-load-section :controller="submission" fluid>
      <template v-slot:default>
        <v-row dense>
          <v-col cols="12" md="9" lg="9" xl="10">
            <ac-asset :asset="submission.x" thumb-name="gallery" :contain="true" :editing="editing"
                      :alt="submissionAltText"
                      :transition="false"
                      v-model="showEditAsset">
              <template v-slot:edit-menu>
                <ac-expanded-property v-model="showEditAsset" aria-label="Edit file dialog" v-if="controls">
                  <v-tabs v-model="editAssetTab">
                    <v-tab>Edit File</v-tab>
                    <v-tab>Preview Listing</v-tab>
                  </v-tabs>
                  <v-window v-model="editAssetTab" class="pt-2">
                    <v-window-item>
                      <ac-patch-field
                          field-type="ac-uppy-file"
                          :patcher="submission.patchers.file"
                          :uppy-id="`submission-${submissionId}-update`"
                          label="Upload a file for this submission"
                      />
                    </v-window-item>
                    <v-window-item>
                      <v-row no-gutters>
                        <v-col class="d-flex" cols="12" sm="6">
                          <v-row no-gutters class="justify-content" align="center">
                            <v-col>
                              <ac-patch-field
                                  field-type="ac-uppy-file"
                                  :patcher="submission.patchers.preview"
                                  label="Preview Image"
                                  :uppy-id="`submission-${submissionId}-update-preview`"
                                  :show-reset="false" :show-clear="true"
                              />
                            </v-col>
                          </v-row>
                        </v-col>
                        <v-col cols="12" sm="6">
                          <ac-gallery-preview :submission="submission.x"/>
                        </v-col>
                      </v-row>
                    </v-window-item>
                  </v-window>
                </ac-expanded-property>
              </template>
            </ac-asset>
          </v-col>
          <v-col cols="12" md="3" lg="3" xl="2">
            <v-col>
              <v-row dense>
                <v-col cols="5" sm="6" md="12" lg="5" :class="{sm3: commissionLink, sm6: !commissionLink}" v-if="!restrictedDownload">
                  <v-btn variant="flat" block @click="submission.patch({favorites: !submission.x!.favorites})"
                         color="secondary">
                    <v-icon left v-if="favorite" :icon="mdiHeart"/>
                    <v-icon left v-else :icon="mdiHeartOutline"/>
                    Fav
                  </v-btn>
                </v-col>
                <v-col cols="7" sm="6" md="12" lg="7" :class="{sm4: commissionLink, sm6: !commissionLink}" v-if="!restrictedDownload">
                  <v-row no-gutters>
                    <v-col cols="6" class="pr-1">
                      <v-btn color="primary" variant="flat" block :href="submission.x!.file.full" download>
                        <v-icon left :icon="mdiContentSaveOutline"/>
                        Save
                      </v-btn>
                    </v-col>
                    <v-col cols="6" class="pl-1">
                      <v-btn color="primary" variant="flat" block :href="submission.x!.file.full" class=".rounded-e">
                        <v-icon left :icon="mdiEye"/>
                        View
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="12" v-if="commissionLink">
                  <v-btn color="green" variant="flat" block :to="submission.x!.commission_link || undefined">
                    <v-icon left :icon="mdiPalette"/>
                    Commission me!
                  </v-btn>
                </v-col>
                <v-col cols="12">
                  <ac-share-button block :title="title" :media-url="shareMediaUrl" :clean="shareMediaClean">
                    <template v-slot:title>
                      Share {{submission.x!.title}}
                    </template>
                    <template v-slot:footer v-if="controls">
                      <ac-load-section :controller="sharedWith">
                        <ac-share-manager :controller="sharedWith"/>
                      </ac-load-section>
                    </template>
                  </ac-share-button>
                </v-col>
              </v-row>
            </v-col>
            <v-col>
              <ac-tag-display :patcher="submission.patchers.tags"
                              :editable="tagControls"
                              :username="submission.x!.owner.username"
                              scope="Submissions"
              />
            </v-col>
            <v-col>
              <ac-artist-display :controller="artists" :submission-id="submissionId"
                                 :editable="tagControls"/>
            </v-col>
            <v-col>
              <ac-character-display :controller="characters" :submission-id="submissionId"
                                    :editable="tagControls"/>
            </v-col>
            <v-col class="pt-2">
              <h3>You might also like...</h3>
              <v-row no-gutters>
                <v-col cols="4" sm="2" lg="6" xl="4" v-for="submission in recommended.list" :key="submission.x!.id">
                  <ac-gallery-preview
                      :submission="submission.x"
                      :show-footer="false"
                      :text="false"
                  />
                </v-col>
              </v-row>
            </v-col>
          </v-col>
          <v-container class="pt-3">
            <v-toolbar :density="editing ? 'default' : 'compact'" color="black">
              <v-toolbar-title v-show="!editing" class="wrap">{{submission.x!.title}}</v-toolbar-title>
              <ac-patch-field label="Title" :patcher="submission.patchers.title"
                              v-if="controls" v-show="editing"/>
              <v-toolbar-items>
                <v-col class="hidden-xs-only mr-0 pr-1" align-self="center">
                  <ac-avatar :user="submission.x!.owner" :show-name="false"/>
                </v-col>
                <v-col class="hidden-xs-only ml-0 pl-0 pr-1" align-self="center">
                  <v-toolbar-title>
                    <ac-link :to="profileLink(submission.x!.owner)">{{submission.x!.owner.username}}</ac-link>
                  </v-toolbar-title>
                </v-col>
                <v-menu offset-x left v-if="controls" :close-on-content-click="false" :attach="$menuTarget">
                  <template v-slot:activator="{props}">
                    <v-btn icon v-bind="props" class="more-button" aria-label="Actions">
                      <v-icon :icon="mdiDotsHorizontal"/>
                    </v-btn>
                  </template>
                  <v-list dense>
                    <v-list-item @click.stop="editing = !editing">
                      <template v-slot:prepend>
                        <v-icon v-if="editing" :icon="mdiLock"/>
                        <v-icon v-else :icon="mdiPencil"/>
                      </template>
                      <v-list-item-title v-if="editing">Lock</v-list-item-title>
                      <v-list-item-title v-else>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-switch v-model="submission.patchers.private.model"
                                  :hide-details="true"
                                  color="primary"
                        />
                      </template>
                      <v-list-item-title>
                        Private
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-switch v-model="submission.patchers.comments_disabled.model"
                                  :hide-details="true"
                                  color="primary"
                        />
                      </template>
                      <v-list-item-title>
                        Comments Disabled
                      </v-list-item-title>
                    </v-list-item>
                    <ac-confirmation :action="deleteSubmission">
                      <template v-slot:default="confirmContext">
                        <v-list-item v-on="confirmContext.on">
                          <template v-slot:prepend>
                            <v-icon class="delete-button" :icon="mdiDelete"/>
                          </template>
                          <v-list-item-title>Delete</v-list-item-title>
                        </v-list-item>
                      </template>
                    </ac-confirmation>
                  </v-list>
                </v-menu>
              </v-toolbar-items>
            </v-toolbar>
            <v-card>
              <v-card-text>
                <v-row no-gutters>
                  <v-col cols="12" md="8" xl="9">
                    <ac-rendered :value="submission.x!.caption" v-show="!editing"/>
                    <ac-patch-field
                        field-type="ac-editor"
                        :auto-save="false"
                        :patcher="submission.patchers.caption"
                        v-if="controls"
                        v-show="editing"
                        label="Description"
                        hint="Describe this piece-- how it came to be, how it makes you feel, or give it a caption."
                        :save-comparison="submission.x!.caption"/>
                  </v-col>
                  <v-col cols="12" md="3" xl="2" offset-md="1">
                    <v-row no-gutters>
                      <v-col cols="12">
                        <h3>Info</h3>
                        <v-divider/>
                      </v-col>
                      <v-col class="hidden-sm-and-up" cols="4" :class="{'d-flex': $vuetify.display.xs}">
                        <v-row no-gutters class="justify-content" align="center">
                          <strong>Submitted by:</strong>
                        </v-row>
                      </v-col>
                      <v-col class="pt-2 hidden-sm-and-up" cols="8">
                        <ac-avatar :user="submission.x!.owner"/>
                      </v-col>
                      <v-col cols="4"><strong>Views:</strong></v-col>
                      <v-col class="text-center" cols="8">{{submission.x!.hits}}</v-col>
                      <v-col cols="4"><strong>Created on:</strong></v-col>
                      <v-col class="text-center" cols="8">{{formatDateTime(submission.x!.created_on)}}</v-col>
                      <v-col cols="4"><strong>Favorites:</strong></v-col>
                      <v-col class="text-center" cols="8">{{submission.x!.favorite_count}}</v-col>
                      <v-col cols="4" v-if="submission.x!.order && controls"><strong>From Deliverable:</strong></v-col>
                      <v-col class="text-center" cols="8" v-if="submission.x!.order && controls">
                        <router-link
                            :to="{name: 'SaleDeliverable', params: {username: submission.x!.owner.username, orderId: submission.x!.order.order_id, deliverableId: submission.x!.order.deliverable_id}}">
                          {{submission.x!.order.deliverable_id}} from order {{submission.x!.order.order_id}}
                        </router-link>
                      </v-col>
                      <v-col class="text-center" cols="12">
                        <ac-rating-button class="mx-0" :controls="controls" :patcher="submission.patchers.rating" variant="flat" size="small" :editing="editing" />
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-container>
          <v-col cols="12">
            <ac-comment-section :commentList="comments" :nesting="true" :locked="locked"/>
          </v-col>
        </v-row>
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
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Submission from '@/types/Submission.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import Formatting from '@/mixins/formatting.ts'
import {ListController} from '@/store/lists/controller.ts'
import {Journal} from '@/types/Journal.ts'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {RATING_COLOR, RATINGS_SHORT, setMetaContent, updateTitle} from '@/lib/lib.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import Editable from '@/mixins/editable.ts'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRelatedManager from '@/components/wrappers/AcRelatedManager.vue'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcArtistDisplay from './AcArtistDisplay.vue'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import {Character} from '@/store/characters/types/Character.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcShareButton from '@/components/AcShareButton.vue'
import AcShareManager from '@/components/AcShareManager.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Sharable from '@/mixins/sharable.ts'
import {
  mdiContentSaveOutline,
  mdiDelete,
  mdiDotsHorizontal,
  mdiEye,
  mdiHeart,
  mdiHeartOutline,
  mdiLock,
  mdiPalette,
  mdiPencil,
} from '@mdi/js'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import {posse} from '@/lib/otherFormatters.ts'
import AcRatingButton from '@/components/AcRatingButton.vue'

@Component({
  components: {
    AcLink,
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
    AcAvatar,
    AcCommentSection,
    AcTagDisplay,
    AcAsset,
    AcLoadSection,
    AcRatingButton,
  },
})
class SubmissionDetail extends mixins(Viewer, Formatting, Editable, Sharable) {
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
  public mdiPencil = mdiPencil
  public mdiDelete = mdiDelete
  public mdiLock = mdiLock
  public mdiDotsHorizontal = mdiDotsHorizontal
  public mdiPalette = mdiPalette
  public mdiEye = mdiEye
  public mdiContentSaveOutline = mdiContentSaveOutline
  public mdiHeartOutline = mdiHeartOutline
  public mdiHeart = mdiHeart

  public get url() {
    return `/api/profiles/submission/${this.submissionId}/`
  }

  public get submissionAltText() {
    if (!this.submission.x) {
      return ''
    }
    if (!this.submission.x.title) {
      return 'Untitled Submission'
    }
    return `Submission entitled: ${this.submission.x.title}`
  }

  public get favorite() {
    return this.submission.x && this.submission.x.favorites
  }

  public get restrictedDownload() {
    if (!this.submission.x) {
      return false
    }
    if (this.theocraticBan && this.submission.x.rating > Ratings.GENERAL) {
      return true
    }
    return false
  }

  public get controls() {
    // istanbul ignore if
    if (!this.submission.x) {
      return false
    }
    return this.isStaff || (this.submission.x.owner.username === this.rawViewerName)
  }

  public get title() {
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
    return title
  }

  public get windowTitle() {
    let title = this.title
    title += ' - (Artconomy.com)'
    return title
  }

  public get tagControls() {
    const submission = this.submission.x as Submission
    return (this.controls || submission.owner.taggable) && this.isRegistered
  }

  @Watch('submission.x.rating')
  public runAgeCheck(value: number) {
    if (value) {
      this.ageCheck({value})
    }
  }

  public get commissionLink() {
    /* istanbul ignore if */
    if (!this.submission.x) {
      return null
    }
    return this.submission.x.commission_link
  }

  public get locked() {
    return !(this.submission.x) || this.submission.x.comments_disabled
  }

  public get shareMedia() {
    return this.submission.x as Submission
  }

  public setMeta(submission: Submission | null | false) {
    if (!submission) {
      return
    }
    updateTitle(this.windowTitle)
    setMetaContent('description', this.textualize(submission.caption).slice(0, 160))
  }

  @Watch('submission.x')
  public submissionMeta(submission: Submission | null) {
    this.setMeta(submission)
  }

  @Watch('submission.x')
  public artistMeta(submission: Submission | null) {
    this.setMeta(this.submission.x)
  }

  public showRating() {
    if (this.editing) {
      this.ratingDialog = true
    }
  }

  public async deleteSubmission() {
    const submission = this.submission.x as Submission
    return this.submission.delete().then(() => {
      this.$router.replace({
        name: 'Profile',
        params: {username: submission.owner.username},
      })
    })
  }

  public created() {
    this.submission = this.$getSingle(
        `submission__${this.submissionId}`, {
          endpoint: this.url,
          params: {view: 'true'},
          socketSettings: {
            appLabel: 'profiles',
            modelName: 'Submission',
            serializer: 'SubmissionSerializer',
          },
        },
    )
    this.artists = this.$getList(`submission__${this.submissionId}__artists`, {
      endpoint: `${this.url}artists/`,
      paginated: false,
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
          endpoint: `/api/lib/comments/profiles.Submission/${this.submissionId}/`,
          reverse: true,
          grow: true,
          params: {size: 5},
        })
    this.recommended = this.$getList(
        `submission-${this.submissionId}-recommended`, {
          endpoint: `${this.url}recommended/`,
          params: {size: 6},
        })
    this.editAsset = this.$getForm(
        `submission__${this.submissionId}`, {
          endpoint: this.url,
          fields: {
            file: {value: ''},
            preview: {value: ''},
          },
          method: 'patch',
        },
    )
    this.submission.get().catch(this.setError)
    this.artists.firstRun()
    this.characters.firstRun()
    this.sharedWith.firstRun().catch(this.statusOk(403))
    this.recommended.firstRun()
    this.$listenForSingle(`submission-${this.submissionId}-update-preview`)
    this.$listenForSingle(`submission-${this.submissionId}-update`)
  }
}

export default toNative(SubmissionDetail)
</script>
