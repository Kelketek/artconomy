<template>
  <v-row :key="submissionId" no-gutters>
    <v-col cols="12">
      <ac-gallery-preview
        class="pa-1"
        :linked="false"
        :submission="submission.x!"
        :show-footer="true"
        :force-hidden="tag.x!.hidden"
      />
    </v-col>
    <v-col cols="12">
      <v-btn
        color="primary"
        block
        variant="elevated"
        @click="showSettings = true"
      >
        Settings
      </v-btn>
      <ac-expanded-property v-model="showSettings" :large="true" :eager="false">
        <template #title>
          <span>Edit Settings</span>
        </template>
        <template #default>
          <v-col v-if="!isOwner" cols="12">
            <v-alert type="info">
              Some options are not available because you are not the submitter
              of this piece.
            </v-alert>
          </v-col>
          <v-row>
            <v-col cols="12" md="6">
              <ac-patch-field
                field-type="v-checkbox"
                label="Unlisted"
                :persistent-hint="true"
                :false-value="false"
                hint="If checked, does not show this piece in your gallery.
              However, people with the link will still be able to view it. To nake it
              unviewable, make sure the 'private' setting is checked."
                :patcher="tag.patchers.hidden"
              />
            </v-col>
            <v-col cols="12" md="6" class="text-center">
              <ac-confirmation :action="tag.delete">
                <template #default="confirmContext">
                  <v-btn
                    color="danger"
                    variant="elevated"
                    v-on="confirmContext.on"
                  >
                    Untag me
                  </v-btn>
                </template>
                <template #confirmation-text>
                  <p v-if="isOwner">
                    This piece will remain in your collection. You can retag it
                    later.
                  </p>
                  <p v-else>
                    <strong>
                      This piece was submitted by someone else. It may be
                      difficult to find it and retag yourself again.
                    </strong>
                  </p>
                </template>
              </ac-confirmation>
              <p>Removes you as the tagged artist from this submission.</p>
            </v-col>
            <v-col cols="12" md="6">
              <ac-patch-field
                field-type="v-checkbox"
                label="Private"
                :persistent-hint="true"
                hint="If checked, this submission is hidden from view.
                  Only you and those you share it with will be able to see it."
                :disabled="!isOwner"
                :patcher="submission.patchers.private"
                :save-indicator="isOwner"
              />
            </v-col>
            <v-col cols="12" md="6" class="text-center">
              <ac-confirmation :action="deleteSubmission">
                <template #default="confirmContext">
                  <v-btn
                    color="danger"
                    :disabled="!isOwner"
                    variant="elevated"
                    v-on="confirmContext.on"
                  >
                    Delete Submission
                  </v-btn>
                </template>
              </ac-confirmation>
              <p>Deletes this submission.</p>
            </v-col>
            <v-col cols="12" class="text-center">
              <v-btn
                class="success"
                :to="{
                  name: 'Submission',
                  params: { submissionId: submission.x!.id },
                }"
                variant="flat"
              >
                Visit Submission
              </v-btn>
            </v-col>
          </v-row>
        </template>
      </ac-expanded-property>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import { SingleController } from "@/store/singles/controller.ts"
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import { useSingle } from "@/store/singles/hooks.ts"
import { computed, ref } from "vue"
import type { ArtistTag, Submission } from "@/types/main"

declare interface ArtistTagManagerProps {
  tag: SingleController<ArtistTag>
  username: string
}

const props = defineProps<ArtistTagManagerProps>()

const tag = props.tag

const submissionId = computed(() => props.tag.x!.submission.id)

const showSettings = ref(false)

const submission = useSingle<Submission>(`submission-${submissionId.value}`, {
  endpoint: `/api/profiles/submission/${submissionId.value}/`,
  x: tag.x!.submission,
})

const isOwner = computed(() => props.username === submission.x?.owner.username)

const deleteSubmission = async () => {
  submission.delete().then(() => {
    tag.deleted = true
  })
}
</script>
