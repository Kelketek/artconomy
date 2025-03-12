<template>
  <ac-load-section :controller="subjectHandler.user">
    <template #default>
      <v-container v-if="subject" fluid>
        <v-row dense class="fill-height">
          <v-col cols="12" :md="subject.artist_mode ? 4 : 8" order="1">
            <v-card>
              <v-card-text>
                <h2>About {{ username }}</h2>
                <v-row v-if="badges" dense>
                  <v-col v-if="subject.stars">
                    <router-link
                      v-if="subject.stars"
                      :to="{ name: 'Ratings', params: { username } }"
                    >
                      <v-rating
                        v-if="subject.stars"
                        :model-value="starRound(subject.stars)"
                        density="compact"
                        size="small"
                        half-increments
                        color="primary"
                        readonly
                      />
                    </router-link>
                  </v-col>
                  <v-col cols="12">
                    <v-chip
                      v-for="badge in badges"
                      :key="badge.label"
                      :color="badge.color"
                      variant="flat"
                      class="mr-1"
                      size="small"
                      :light="badge.light"
                    >
                      <strong>{{ badge.label }}</strong>
                    </v-chip>
                  </v-col>
                </v-row>
                <small
                  ><strong>Views:</strong> {{ subject.hits }}
                  <strong>Watchers: </strong>{{ subject.watches }}</small
                >
                <ac-patch-field
                  v-show="editing"
                  v-if="controls"
                  field-type="ac-editor"
                  :patcher="userHandler.patchers.biography"
                />
                <div v-show="!editing">
                  <ac-rendered :value="subject.biography" :truncate="true">
                    <template #empty>
                      <v-col v-if="isCurrent" class="text-center">
                        You haven't added any profile information yet.
                        <v-btn
                          block
                          color="green"
                          variant="flat"
                          @click="() => (editing = true)"
                        >
                          Add some.
                        </v-btn>
                      </v-col>
                    </template>
                  </ac-rendered>
                </div>
                <v-btn
                  v-if="
                    subjectHandler.artistProfile.x &&
                    subject.artist_mode &&
                    subjectHandler.artistProfile.x.public_queue
                  "
                  block
                  color="secondary"
                  :to="{ name: 'Queue', params: { username } }"
                >
                  <v-icon left :icon="mdiTrayFull" />
                  View Artist Queue
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col
            v-if="subject.artist_mode"
            cols="12"
            md="8"
            order="2"
            class="justify-center"
          >
            <v-col>
              <ac-subjective-product-list
                :username="username"
                :mini="true"
                :hide-new-button="true"
              />
            </v-col>
            <v-col align-self="end">
              <v-btn
                block
                color="green"
                :to="{ name: 'Products', params: { username } }"
                variant="flat"
              >
                View full store
              </v-btn>
            </v-col>
          </v-col>
          <v-col
            cols="12"
            :md="subject.artist_mode ? 8 : 12"
            :order="subject.artist_mode ? 2 : 3"
          >
            <v-card>
              <v-card-text>
                <v-card-title
                  >{{ username }}'s {{ artList.label }}</v-card-title
                >
                <submission-list
                  :list-name="artList.listName"
                  :endpoint="artList.endpoint"
                  :username="username"
                  :empty-message="artList.emptyMessage"
                  :track-pages="false"
                  :show-pagination="false"
                />
                <v-btn
                  block
                  :to="artList.buttonDest"
                  color="green"
                  class="mt-2"
                  variant="flat"
                >
                  {{ artList.buttonText }}
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="4" :order="subject.artist_mode ? 4 : 2">
            <ac-journals :username="username" />
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import { useSubject } from "@/mixins/subjective.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcRendered from "@/components/wrappers/AcRendered.ts"
import AcJournals from "@/components/AcJournals.vue"
import { useEditable } from "@/mixins/editable.ts"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcSubjectiveProductList from "@/components/views/store/AcSubjectiveProductList.vue"
import { starRound } from "@/lib/lib.ts"
import SubmissionList from "@/components/views/profile/SubmissionList.vue"
import { SingleController } from "@/store/singles/controller.ts"
import { mdiTrayFull } from "@mdi/js"
import { computed } from "vue"
import type { SubjectiveProps } from "@/types/main"
import { User } from "@/store/profiles/types/main"

declare interface ProfileBadge {
  label: string
  color: string
  light: boolean
}

const props = defineProps<SubjectiveProps>()
const { subject, subjectHandler, controls, isCurrent } = useSubject({ props })
const { editing } = useEditable(controls)

const badges = computed(() => {
  const badges: ProfileBadge[] = []
  if (!subjectHandler.artistProfile.x) {
    return badges
  }
  if (subjectHandler.artistProfile.x.lgbt) {
    badges.push({
      label: "LGBTQ+",
      color: "purple",
      light: false,
    })
  }
  if (subjectHandler.artistProfile.x.artist_of_color) {
    badges.push({
      label: "Artist of Color",
      color: "orange",
      light: true,
    })
  }
  if (subject.value && subject.value.landscape) {
    // TODO: Make this more dynamic per plan name and less hard coded.
    badges.push({
      label: "Landscape Subscriber",
      color: "green",
      light: true,
    })
  }
  return badges
})

const userHandler = computed(() => {
  return subjectHandler.user as SingleController<User>
})

const artList = computed(() => {
  let buttonText: string

  if (subject.value?.artist_mode) {
    if (isCurrent.value) {
      buttonText = "Manage my art"
    } else {
      buttonText = "View full gallery"
    }
    return {
      listName: "art",
      label: "Art",
      endpoint: `/api/profiles/account/${props.username}/submissions/art/`,
      emptyMessage: isCurrent.value
        ? "You have not yet uploaded any art where you are tagged as the artist."
        : "This artist has not yet uploaded any art.",
      buttonText: buttonText,
      buttonDest: {
        name: "Gallery",
        params: { username: props.username },
      },
    }
  }
  if (isCurrent.value) {
    buttonText = "Manage my collection"
  } else {
    buttonText = "View full collection"
  }
  return {
    listName: "collection",
    label: "Collection",
    endpoint: `/api/profiles/account/${props.username}/submissions/collection/`,
    emptyMessage: isCurrent.value
      ? "You have not uploaded any art to your collection. Your collection " +
        "holds all art artists have made for you."
      : "This user has not uploaded any art to their collection. Their collection holds all art artists have made for them.",
    buttonText: buttonText,
    buttonDest: {
      name: "Collection",
      params: { username: props.username },
    },
  }
})
</script>
