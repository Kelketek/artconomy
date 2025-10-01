<template>
  <v-container fluid>
    <ac-load-section :controller="submission" fluid>
      <template #default>
        <v-row dense>
          <v-col cols="12" md="9" lg="9" xl="10">
            <ac-asset
              v-model="showEditAsset"
              :asset="submission.x"
              thumb-name="gallery"
              :contain="true"
              :editing="editing"
              :alt="submissionAltText"
              :transition="false"
            >
              <template #edit-menu>
                <ac-expanded-property
                  v-if="controls"
                  v-model="showEditAsset"
                  aria-label="Edit file dialog"
                >
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
                          <v-row
                            no-gutters
                            class="justify-content"
                            align="center"
                          >
                            <v-col>
                              <ac-patch-field
                                field-type="ac-uppy-file"
                                :patcher="submission.patchers.preview!"
                                label="Preview Image"
                                :uppy-id="`submission-${submissionId}-update-preview`"
                                :show-reset="false"
                                :show-clear="true"
                              />
                            </v-col>
                          </v-row>
                        </v-col>
                        <v-col cols="12" sm="6">
                          <ac-gallery-preview :submission="submission.x!" />
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
                <v-col
                  v-if="!restrictedDownload"
                  cols="5"
                  sm="6"
                  md="12"
                  lg="5"
                  :class="{ sm3: commissionLink, sm6: !commissionLink }"
                >
                  <v-btn
                    variant="flat"
                    block
                    color="secondary"
                    @click="
                      submission.patch({ favorites: !submission.x!.favorites })
                    "
                  >
                    <v-icon v-if="favorite" left :icon="mdiHeart" />
                    <v-icon v-else left :icon="mdiHeartOutline" />
                    Fav
                  </v-btn>
                </v-col>
                <v-col
                  v-if="!restrictedDownload && submission.x!.file"
                  cols="7"
                  sm="6"
                  md="12"
                  lg="7"
                  :class="{ sm4: commissionLink, sm6: !commissionLink }"
                >
                  <v-row no-gutters>
                    <v-col cols="6" class="pr-1">
                      <v-btn
                        color="primary"
                        variant="flat"
                        block
                        :href="submission.x!.file.full"
                        download
                      >
                        <v-icon left :icon="mdiContentSaveOutline" />
                        Save
                      </v-btn>
                    </v-col>
                    <v-col cols="6" class="pl-1">
                      <v-btn
                        color="primary"
                        variant="flat"
                        block
                        :href="submission.x!.file.full"
                        class=".rounded-e"
                      >
                        <v-icon left :icon="mdiEye" />
                        View
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col v-if="commissionLink" cols="12">
                  <v-btn
                    color="green"
                    variant="flat"
                    block
                    :to="submission.x!.commission_link || undefined"
                  >
                    <v-icon left :icon="mdiPalette" />
                    Commission me!
                  </v-btn>
                </v-col>
                <v-col cols="12">
                  <ac-share-button
                    block
                    :title="title"
                    :media-url="shareMediaUrl"
                    :clean="shareMediaClean"
                  >
                    <template #title>
                      Share {{ submission.x!.title }}
                    </template>
                    <template v-if="controls" #footer>
                      <ac-load-section :controller="sharedWith">
                        <ac-share-manager :controller="sharedWith" />
                      </ac-load-section>
                    </template>
                  </ac-share-button>
                </v-col>
              </v-row>
            </v-col>
            <v-col>
              <ac-tag-display
                :patcher="submission.patchers.tags"
                :editable="tagControls"
                :username="submission.x!.owner.username"
                scope="Submissions"
              />
            </v-col>
            <v-col>
              <ac-artist-display
                :controller="artists"
                :submission-id="submissionId"
                :editable="tagControls"
              />
            </v-col>
            <v-col>
              <ac-character-display
                :controller="characters"
                :submission-id="submissionId"
                :editable="tagControls"
              />
            </v-col>
            <v-col class="pt-2">
              <h3>You might also like...</h3>
              <v-row no-gutters>
                <v-col
                  v-for="recommendedSubmission in recommended.list"
                  :key="recommendedSubmission.x!.id"
                  cols="4"
                  sm="2"
                  lg="6"
                  xl="4"
                >
                  <ac-gallery-preview
                    :submission="recommendedSubmission.x!"
                    :show-footer="false"
                    :text="false"
                  />
                </v-col>
              </v-row>
            </v-col>
          </v-col>
          <v-container class="pt-3">
            <v-toolbar :density="editing ? 'default' : 'compact'" color="black">
              <v-toolbar-title v-show="!editing" class="wrap">
                {{ submission.x!.title }}
              </v-toolbar-title>
              <ac-patch-field
                v-if="controls"
                v-show="editing"
                label="Title"
                :patcher="submission.patchers.title"
              />
              <v-toolbar-items>
                <v-col class="hidden-xs-only mr-0 pr-1" align-self="center">
                  <ac-avatar :user="submission.x!.owner" :show-name="false" />
                </v-col>
                <v-col
                  class="hidden-xs-only ml-0 pl-0 pr-1"
                  align-self="center"
                >
                  <v-toolbar-title>
                    <ac-link :to="profileLink(submission.x!.owner)">
                      {{ submission.x!.owner.username }}
                    </ac-link>
                  </v-toolbar-title>
                </v-col>
                <v-menu
                  v-if="controls"
                  offset-x
                  left
                  :close-on-content-click="false"
                  :attach="menuTarget"
                >
                  <template #activator="activator">
                    <v-btn
                      icon
                      v-bind="activator.props"
                      class="more-button"
                      aria-label="Actions"
                    >
                      <v-icon :icon="mdiDotsHorizontal" />
                    </v-btn>
                  </template>
                  <v-list dense>
                    <v-list-item @click.stop="editing = !editing">
                      <template #prepend>
                        <v-icon v-if="editing" :icon="mdiLock" />
                        <v-icon v-else :icon="mdiPencil" />
                      </template>
                      <v-list-item-title v-if="editing">
                        Lock
                      </v-list-item-title>
                      <v-list-item-title v-else> Edit </v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template #prepend>
                        <v-switch
                          v-model="submission.patchers.private.model"
                          :hide-details="true"
                          color="primary"
                        />
                      </template>
                      <v-list-item-title> Private </v-list-item-title>
                    </v-list-item>
                    <v-list-item>
                      <template #prepend>
                        <v-switch
                          v-model="submission.patchers.comments_disabled.model"
                          :hide-details="true"
                          color="primary"
                        />
                      </template>
                      <v-list-item-title> Comments Disabled </v-list-item-title>
                    </v-list-item>
                    <ac-confirmation :action="deleteSubmission">
                      <template #default="confirmContext">
                        <v-list-item v-on="confirmContext.on">
                          <template #prepend>
                            <v-icon class="delete-button" :icon="mdiDelete" />
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
                    <ac-rendered
                      v-show="!editing"
                      :value="submission.x!.caption"
                    />
                    <ac-patch-field
                      v-if="controls"
                      v-show="editing"
                      field-type="ac-editor"
                      :auto-save="false"
                      :patcher="submission.patchers.caption"
                      label="Description"
                      hint="Describe this piece-- how it came to be, how it makes you feel, or give it a caption."
                      :save-comparison="submission.x!.caption"
                    />
                  </v-col>
                  <v-col cols="12" md="3" xl="2" offset-md="1">
                    <v-row no-gutters>
                      <v-col cols="12">
                        <h3>Info</h3>
                        <v-divider />
                      </v-col>
                      <v-col
                        class="hidden-sm-and-up"
                        cols="4"
                        :class="{ 'd-flex': xs }"
                      >
                        <v-row
                          no-gutters
                          class="justify-content"
                          align="center"
                        >
                          <strong>Submitted by:</strong>
                        </v-row>
                      </v-col>
                      <v-col class="pt-2 hidden-sm-and-up" cols="8">
                        <ac-avatar :user="submission.x!.owner" />
                      </v-col>
                      <v-col cols="4">
                        <strong>Views:</strong>
                      </v-col>
                      <v-col class="text-center" cols="8">
                        {{ submission.x!.hits }}
                      </v-col>
                      <v-col cols="4">
                        <strong>Created on:</strong>
                      </v-col>
                      <v-col class="text-center" cols="8">
                        {{ formatDateTime(submission.x!.created_on) }}
                      </v-col>
                      <v-col cols="4">
                        <strong>Favorites:</strong>
                      </v-col>
                      <v-col class="text-center" cols="8">
                        {{ submission.x!.favorite_count }}
                      </v-col>
                      <v-col v-if="submission.x!.order && controls" cols="4">
                        <strong>From Deliverable:</strong>
                      </v-col>
                      <v-col
                        v-if="submission.x!.order && controls"
                        class="text-center"
                        cols="8"
                      >
                        <router-link
                          :to="{
                            name: 'SaleDeliverable',
                            params: {
                              username: submission.x!.owner.username,
                              orderId: submission.x!.order.order_id,
                              deliverableId: submission.x!.order.deliverable_id,
                            },
                          }"
                        >
                          {{ submission.x!.order.deliverable_id }} from order
                          {{ submission.x!.order.order_id }}
                        </router-link>
                      </v-col>
                      <v-col class="text-center" cols="12">
                        <ac-rating-button
                          class="mx-0"
                          :controls="controls"
                          :patcher="submission.patchers.rating"
                          variant="flat"
                          size="small"
                          :editing="editing"
                        />
                      </v-col>
                      <v-col class="text-center" cols="12">
                        <ac-report-button v-if="!isCurrent" />
                        <ac-kill-button
                          v-if="powers.moderate_content"
                          :controller="submission"
                        />
                      </v-col>
                    </v-row>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-container>
          <v-col cols="12">
            <ac-comment-section
              :comment-list="comments"
              :nesting="true"
              :locked="locked"
            />
          </v-col>
        </v-row>
      </template>
    </ac-load-section>
  </v-container>
</template>

<script setup lang="ts">
import { adultTag, useViewer } from "@/mixins/viewer.ts"
import { useDisplay } from "vuetify"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcAsset from "@/components/AcAsset.vue"
import AcTagDisplay from "@/components/AcTagDisplay.vue"
import AcCommentSection from "@/components/comments/AcCommentSection.vue"
import { setMetaContent, updateTitle } from "@/lib/lib.ts"
import AcAvatar from "@/components/AcAvatar.vue"
import { useEditable } from "@/mixins/editable.ts"
import AcRendered from "@/components/wrappers/AcRendered.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcArtistDisplay from "./AcArtistDisplay.vue"
import AcCharacterDisplay from "@/components/views/submission/AcCharacterDisplay.vue"
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import AcShareButton from "@/components/AcShareButton.vue"
import AcShareManager from "@/components/AcShareManager.vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import { useSharable } from "@/mixins/sharable.ts"
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
} from "@mdi/js"
import { Ratings } from "@/types/enums/Ratings.ts"
import { formatDateTime, posse, profileLink } from "@/lib/otherFormatters.ts"
import AcRatingButton from "@/components/AcRatingButton.vue"
import { computed, ref, watch } from "vue"
import { listenForSingle, useSingle } from "@/store/singles/hooks.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { useRouter } from "vue-router"
import { textualize } from "@/lib/markdown.ts"
import { useTargets } from "@/plugins/targets.ts"
import type {
  ArtistTag,
  Comment,
  LinkedCharacter,
  RatingsValue,
  Submission,
} from "@/types/main"
import { TerseUser, RelatedUser } from "@/store/profiles/types/main"
import AcReportButton from "@/components/AcReportButton.vue"
import AcKillButton from "@/components/AcKillButton.vue"

const props = defineProps<{ submissionId: string }>()

const showEditAsset = ref(false)
const editAssetTab = ref(0)
const { viewer, theocraticBan, rawViewerName, powers, isRegistered, ageCheck } =
  useViewer()
const { menuTarget } = useTargets()
const router = useRouter()

const url = computed(() => {
  return `/api/profiles/submission/${props.submissionId}/`
})

const submission = useSingle<Submission>(`submission__${props.submissionId}`, {
  endpoint: url.value,
  params: { view: "true" },
  socketSettings: {
    appLabel: "profiles",
    modelName: "Submission",
    serializer: "SubmissionSerializer",
  },
})
const artists = useList<ArtistTag>(
  `submission__${props.submissionId}__artists`,
  {
    endpoint: `${url.value}artists/`,
    paginated: false,
  },
)
const characters = useList<LinkedCharacter>(
  `submission__${props.submissionId}__characters`,
  {
    endpoint: `${url.value}characters/`,
    paginated: false,
  },
)
const sharedWith = useList<TerseUser>(
  `submission__${props.submissionId}__share`,
  {
    endpoint: `${url.value}share/`,
    paginated: false,
  },
)
const comments = useList<Comment>(`submission-${props.submissionId}-comments`, {
  endpoint: `/api/lib/comments/profiles.Submission/${props.submissionId}/`,
  reverse: true,
  grow: true,
  params: { size: 5 },
})
const recommended = useList<Submission>(
  `submission-${props.submissionId}-recommended`,
  {
    endpoint: `${url.value}recommended/`,
    params: { size: 6 },
  },
)

const { setError, statusOk } = useErrorHandling()

submission.get().catch(setError)
artists.firstRun()
characters.firstRun()
sharedWith.firstRun().catch(statusOk(403))
recommended.firstRun()
listenForSingle(`submission-${props.submissionId}-update-preview`)
listenForSingle(`submission-${props.submissionId}-update`)

const submissionAltText = computed(() => {
  if (!submission.x) {
    return ""
  }
  if (!submission.x.title) {
    return "Untitled Submission"
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
  if (!submission.x.file) {
    return false
  }
  return (
    theocraticBan.value &&
    !viewer.value?.verified_adult &&
    submission.x.rating > Ratings.GENERAL
  )
})

const isCurrent = computed(() => {
  // istanbul ignore if
  if (!submission.x) {
    return false
  }
  return submission.x.owner.username === rawViewerName.value
})

const controls = computed(() => {
  return powers.value.moderate_content || isCurrent.value
})

const { editing } = useEditable(controls)

const deleteSubmission = async () => {
  const username = submission.x!.owner.username
  return submission.delete().then(() => {
    router.replace({
      name: "Profile",
      params: { username },
    })
  })
}

const title = computed(() => {
  // istanbul ignore if
  if (!submission.x) {
    return ""
  }
  let title = submission.x.title
  if (title) {
    title += " -- "
  }
  if (artists.list.length) {
    if (title) {
      title += "by "
    } else {
      title += "By "
    }
    const artistNames = artists.list.map(
      (user) => (user.x!.user as RelatedUser).username,
    )
    const firstNames = artistNames.slice(0, 4)
    title += posse(firstNames, artistNames.length - firstNames.length)
  } else {
    title += `Submitted by ${submission.x.owner.username}`
  }
  return title
})

const windowTitle = computed(() => {
  let derivedTitle = title.value
  derivedTitle += " - (Artconomy.com)"
  return derivedTitle
})

const tagControls = computed(() => {
  return !!(
    (controls.value || submission.x?.owner.taggable) &&
    isRegistered.value
  )
})

const commissionLink = computed(() => {
  /* istanbul ignore if */
  if (!submission.x) {
    return null
  }
  return submission.x.commission_link
})

const locked = computed(() => {
  return !submission.x || submission.x.comments_disabled
})

const shareMedia = computed(() => {
  return submission.x as Submission
})

const { xs } = useDisplay()

const { shareMediaUrl, shareMediaClean } = useSharable(shareMedia)

const setMeta = (submissionData: Submission | null | false) => {
  if (!submissionData) {
    return
  }
  updateTitle(windowTitle.value)
  adultTag(submissionData.rating)
  setMetaContent(
    "description",
    textualize(submissionData.caption).slice(0, 160),
  )
}

watch(
  () => submission.x?.rating,
  (value?: RatingsValue | null) => {
    if (value) {
      ageCheck({ value })
    }
  },
)

watch(
  () => submission.x,
  (submissionData: Submission | null) => {
    setMeta(submissionData)
  },
)
</script>

<style>
.wrap {
  white-space: normal;
}
</style>
