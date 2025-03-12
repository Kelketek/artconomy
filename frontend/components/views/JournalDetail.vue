<template>
  <ac-load-section :controller="journal">
    <template #default>
      <v-container v-if="journal.x">
        <v-row>
          <v-col>
            <v-card>
              <v-toolbar dense color="black">
                <ac-avatar
                  :username="username"
                  :show-name="false"
                  class="ml-3"
                />
                <v-toolbar-title class="ml-1">
                  <ac-link :to="profileLink(subject)">
                    {{ username }}
                  </ac-link>
                </v-toolbar-title>
                <v-spacer />
                <v-tooltip bottom>
                  <template #activator="activator">
                    <v-icon v-bind="activator.props" :icon="mdiInformation" />
                  </template>
                  {{ formatDateTime(journal.x.created_on) }}
                  <span v-if="journal.x.edited"
                    ><br />Edited:
                    {{ formatDateTime(journal.x.edited_on) }}</span
                  >
                </v-tooltip>
                <v-menu
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
                    <v-list-item
                      class="edit-toggle"
                      @click.stop="editing = !editing"
                    >
                      <template #prepend>
                        <v-icon v-if="editing" :icon="mdiLock" />
                        <v-icon v-else :icon="mdiPencil" />
                      </template>
                      <v-list-item-title v-if="editing">
                        Lock
                      </v-list-item-title>
                      <v-list-item-title v-else> Edit </v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click.stop="
                        journal.patch({ subscribed: !journal.x.subscribed })
                      "
                    >
                      <template #prepend>
                        <v-icon
                          v-if="journal.x.subscribed"
                          :icon="mdiVolumeHigh"
                        />
                        <v-icon v-else :icon="mdiVolumeOff" />
                      </template>
                      <v-list-item-title>
                        Notifications
                        <span v-if="journal.x.subscribed">on</span>
                        <span v-else>off</span>
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        journal.patchers.comments_disabled.model =
                          !journal.patchers.comments_disabled.model
                      "
                    >
                      <template #prepend>
                        <v-switch
                          :model-value="
                            journal.patchers.comments_disabled.model
                          "
                          color="primary"
                          :hide-details="true"
                        />
                      </template>
                      <v-list-item-title> Comments Disabled </v-list-item-title>
                    </v-list-item>
                    <ac-confirmation v-if="controls" :action="deleteJournal">
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
              </v-toolbar>
              <v-card-text>
                <v-row>
                  <v-col cols="12">
                    <ac-patch-field
                      v-show="editing"
                      v-if="controls"
                      :patcher="journal.patchers.subject"
                    />
                    <h1 v-show="!editing" class="text-h5">
                      <ac-rendered :value="journal.x.subject" :inline="true" />
                    </h1>
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                      v-show="editing"
                      v-if="controls"
                      field-type="ac-editor"
                      :patcher="journal.patchers.body"
                      :auto-save="false"
                    >
                      <template #pre-actions>
                        <v-col class="shrink">
                          <v-tooltip top>
                            <template #activator="activator">
                              <v-btn
                                v-bind="activator.props"
                                icon
                                color="danger"
                                class="cancel-button"
                                @click="editing = false"
                              >
                                <v-icon :icon="mdiLock" />
                              </v-btn>
                            </template>
                            <span>Stop Editing</span>
                          </v-tooltip>
                        </v-col>
                      </template>
                    </ac-patch-field>
                    <ac-rendered v-show="!editing" :value="journal.x.body" />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <ac-comment-section
              :comment-list="journalComments"
              :nesting="true"
              :locked="locked"
            />
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>
<script setup lang="ts">
import { useEditable } from "@/mixins/editable.ts"
import AcAvatar from "@/components/AcAvatar.vue"
import { useSubject } from "@/mixins/subjective.ts"
import AcRendered from "@/components/wrappers/AcRendered.ts"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import AcCommentSection from "@/components/comments/AcCommentSection.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcLink from "@/components/wrappers/AcLink.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import {
  mdiLock,
  mdiPencil,
  mdiVolumeHigh,
  mdiVolumeOff,
  mdiDelete,
  mdiDotsHorizontal,
  mdiInformation,
} from "@mdi/js"
import { useSingle } from "@/store/singles/hooks.ts"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useRouter } from "vue-router"
import { computed } from "vue"
import { formatDateTime, profileLink } from "@/lib/otherFormatters.ts"
import { useTargets } from "@/plugins/targets.ts"
import type { Comment, Journal, SubjectiveProps } from "@/types/main"

const props = defineProps<SubjectiveProps & { journalId: number }>()
const { controls, subject } = useSubject({ props })
const router = useRouter()
const { editing } = useEditable(controls)
const { menuTarget } = useTargets()

const { setError } = useErrorHandling()
const journal = useSingle<Journal>(`journal-${props.journalId}`, {
  endpoint: `/api/profiles/account/${props.username}/journals/${props.journalId}/`,
})
journal.get().catch(setError)
const journalComments = useList<Comment>(
  `journal-${props.journalId}-comments`,
  {
    endpoint: `/api/lib/comments/profiles.Journal/${props.journalId}/`,
    reverse: true,
    grow: true,
    params: { size: 5 },
  },
)
journalComments.firstRun()

const goBack = () => {
  router.push({
    name: "Profile",
    params: { username: props.username },
  })
}

const deleteJournal = async () => {
  return journal.delete().then(goBack)
}

const locked = computed(() => !journal.x || journal.x!.comments_disabled)
</script>
