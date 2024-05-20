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
                                  :patcher="submission.patchers.preview!"
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
                <v-menu offset-x left v-if="controls" :close-on-content-click="false" :attach="menuTarget">
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

<script setup lang="ts">
import {useViewer} from '@/mixins/viewer.ts'
import Submission from '@/types/Submission.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAsset from '@/components/AcAsset.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import Comment from '@/types/Comment.ts'
import {setMetaContent, updateTitle} from '@/lib/lib.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import {useEditable} from '@/mixins/editable.ts'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import AcArtistDisplay from './AcArtistDisplay.vue'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import {Character} from '@/store/characters/types/Character.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcShareButton from '@/components/AcShareButton.vue'
import AcShareManager from '@/components/AcShareManager.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {useSharable} from '@/mixins/sharable.ts'
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
import {Ratings} from '@/types/Ratings.ts'
import {formatDateTime, posse, profileLink} from '@/lib/otherFormatters.ts'
import AcRatingButton from '@/components/AcRatingButton.vue'
import {computed, ref, watch} from 'vue'
import {listenForSingle, useSingle} from '@/store/singles/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useRouter} from 'vue-router'
import {textualize} from '@/lib/markdown.ts'
import {useTargets} from '@/plugins/targets.ts'

const props = defineProps<{submissionId: string}>()

const showEditAsset = ref(false)
const editAssetTab = ref(0)
const {viewer, theocraticBan, rawViewerName, isStaff, isRegistered, ageCheck} = useViewer()
const {menuTarget} = useTargets()
const router = useRouter()

const url = computed(() => {
  return `/api/profiles/submission/${props.submissionId}/`
})

const submission = useSingle<Submission>(
    `submission__${props.submissionId}`, {
      endpoint: url.value,
      params: {view: 'true'},
      socketSettings: {
        appLabel: 'profiles',
        modelName: 'Submission',
        serializer: 'SubmissionSerializer',
      },
    },
)
const artists = useList<TerseUser>(`submission__${props.submissionId}__artists`, {
  endpoint: `${url.value}artists/`,
  paginated: false,
})
const characters = useList<Character>(`submission__${props.submissionId}__characters`, {
  endpoint: `${url.value}characters/`,
  paginated: false,
})
const sharedWith = useList<TerseUser>(`submission__${props.submissionId}__share`, {
  endpoint: `${url.value}share/`,
  paginated: false,
})
const comments = useList<Comment>(
    `submission-${props.submissionId}-comments`, {
      endpoint: `/api/lib/comments/profiles.Submission/${props.submissionId}/`,
      reverse: true,
      grow: true,
      params: {size: 5},
    })
const recommended = useList<Submission>(
    `submission-${props.submissionId}-recommended`, {
      endpoint: `${url.value}recommended/`,
      params: {size: 6},
    })

const {setError, statusOk} = useErrorHandling()

submission.get().catch(setError)
artists.firstRun()
characters.firstRun()
sharedWith.firstRun().catch(statusOk(403))
recommended.firstRun()
listenForSingle(`submission-${props.submissionId}-update-preview`)
listenForSingle(`submission-${props.submissionId}-update`)


const submissionAltText = computed(() => {
  if (!submission.x) {
    return ''
  }
  if (!submission.x.title) {
    return 'Untitled Submission'
  }
  return `Submission entitled: ${submission.x.title}`
})

const favorite = computed(() => {
  return submission.x && submission.x.favorites
})

const restrictedDownload = computed(() => {
  if (!submission.x) {
    return false
  }
  return (theocraticBan.value && !viewer.value?.verified_adult) && submission.x.rating > Ratings.GENERAL;
})

const controls = computed(() => {
  // istanbul ignore if
  if (!submission.x) {
    return false
  }
  return isStaff.value || (submission.x.owner.username === rawViewerName.value)
})

const {editing} = useEditable(controls)

const deleteSubmission = async () => {
  const username = submission.x!.owner.username
  return submission.delete().then(() => {
    router.replace({
      name: 'Profile',
      params: {username},
    })
  })
}

const title = computed(() => {
  // istanbul ignore if
  if (!submission.x) {
    return ''
  }
  let title = submission.x.title
  if (title) {
    title += ' -- '
  }
  if (artists.list.length) {
    if (title) {
      title += 'by '
    } else {
      title += 'By '
    }
    // @ts-ignore
    const artistNames = artists.list.map((user) => (user.x.user as TerseUser).username)
    const firstNames = artistNames.slice(0, 4)
    title += posse(firstNames, artistNames.length - firstNames.length)
  } else {
    title += `Submitted by ${submission.x.owner.username}`
  }
  return title
})

const windowTitle = computed(() => {
  let derivedTitle = title.value
  derivedTitle += ' - (Artconomy.com)'
  return derivedTitle
})

const tagControls = computed(() => {
  return (controls.value || submission.x?.owner.taggable) && isRegistered.value
})

const commissionLink = computed(() => {
  /* istanbul ignore if */
  if (!submission.x) {
    return null
  }
  return submission.x.commission_link
})

const locked = computed(() => {
  return !(submission.x) || submission.x.comments_disabled
})

const shareMedia = computed(() => {
  return submission.x as Submission
})

const {shareMediaUrl, shareMediaClean} = useSharable(shareMedia)

const setMeta = (submissionData: Submission | null | false) => {
  if (!submissionData) {
    return
  }
  updateTitle(windowTitle.value)
  setMetaContent('description', textualize(submissionData.caption).slice(0, 160))
}

watch(() => submission.x?.rating, (value?: Ratings|null) => {
  if (value) {
    ageCheck({value})
  }
})

watch(() => submission.x, (submissionData: Submission|null) => {
  setMeta(submissionData)
})
</script>
