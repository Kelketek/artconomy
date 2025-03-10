<template>
  <ac-load-section
    v-show="character.profile.ready"
    :controller="character.submissions"
  >
    <v-card color="grey-darken-4">
      <v-card-title><h2>Uploads</h2></v-card-title>
      <v-card-text>
        <v-row
          v-if="character.submissions.list.length && character.profile.ready"
          no-gutters
        >
          <div :class="featuredClasses">
            <v-col cols="12">
              <ac-gallery-preview
                :submission="featured!"
                thumb-name="gallery"
                :contain="true"
                :compact="true"
                :aspect-ratio="null"
                :show-footer="lgAndUp"
              />
              <v-col
                v-if="more && mdAndUp"
                class="shrink text-center pt-2"
              >
                <v-btn
                  color="primary"
                  variant="flat"
                  :to="{name: 'CharacterGallery', params: {username, characterName}}"
                >
                  See all
                  Uploads
                </v-btn>
              </v-col>
            </v-col>
          </div>
          <v-col
            cols="12"
            md="4"
            lg="2"
            offset-md="1"
            align-self="center"
          >
            <v-row>
              <v-col
                v-for="submission in prunedSubmissions"
                :key="submission.x!.id"
                cols="6"
                lg="12"
              >
                <ac-gallery-preview
                  :submission="submission.x!"
                  thumb-name="thumbnail"
                  :contain="true"
                  :show-footer="false"
                />
              </v-col>
              <v-col
                v-if="more && smAndDown"
                cols="12"
                class="text-center pt-2"
              >
                <v-btn
                  color="primary"
                  variant="flat"
                  :to="{name: 'CharacterGallery', params: {username, characterName}}"
                >
                  See all
                  Uploads
                </v-btn>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcGalleryPreview from '../../AcGalleryPreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller.ts'
import {useRatingRefresh} from '@/mixins/RatingRefresh.ts'
import {useCharacter} from '@/store/characters/hooks.ts'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'
import type {CharacterProps, Submission} from '@/types/main'

const props = defineProps<CharacterProps>()

const character = useCharacter(props)
const {smAndDown, mdAndUp, lgAndUp} = useDisplay()

character.submissions.firstRun()

useRatingRefresh([character.submissions])

const featured = computed(() => {
  const profile = character.profile.x
  if (!profile) {
    return null
  }
  return profile.primary_submission || character.submissions.list[0]?.x
})

const prunedSubmissions = computed(() => {
  const compare = featured.value?.id
  const submissions = character.submissions.list.filter(
      (submission: SingleController<Submission>) =>
          (submission.x as Submission).id !== compare,
  )
  return submissions.slice(0, 4)
})

const featuredClasses = computed(() => {
  const single = prunedSubmissions.value.length === 0
  return {
    'pb-2': smAndDown.value,
    'v-col-12': true,
    'v-col-md-7': !single,
    'v-col-lg-9': !single,
    'align-self-center': true,
  }
})

const more = computed(() => {
  return (prunedSubmissions.value.length < (character.submissions.list.length - 1))
})
</script>
