<template>
  <ac-load-section :controller="character.submissions" v-show="character.profile.ready">
    <v-card color="grey-darken-4">
      <v-card-title><h2>Uploads</h2></v-card-title>
      <v-card-text>
        <v-row no-gutters v-if="character.submissions.list.length && character.profile.ready"
        >
          <div :class="featuredClasses">
            <v-col cols="12">
              <ac-gallery-preview
                  :submission="featured"
                  thumb-name="gallery"
                  :contain="true"
                  :compact="true"
                  :aspect-ratio="null"
                  :show-footer="$vuetify.display.lgAndUp"
              />
              <v-col class="shrink text-center pt-2" v-if="more && $vuetify.display.mdAndUp">
                <v-btn color="primary" variant="flat" :to="{name: 'CharacterGallery', params: {username, characterName}}">See all
                  Uploads
                </v-btn>
              </v-col>
            </v-col>
          </div>
          <v-col cols="12" md="4" lg="2" offset-md="1" align-self="center">
            <v-row>
              <v-col cols="6" lg="12" v-for="submission in prunedSubmissions" :key="submission.x!.id">
                <ac-gallery-preview
                    :submission="submission.x"
                    thumb-name="thumbnail"
                    :contain="true"
                    :show-footer="false"
                />
              </v-col>
              <v-col cols="12" class="text-center pt-2" v-if="more && $vuetify.display.smAndDown">
                <v-btn color="primary" variant="flat" :to="{name: 'CharacterGallery', params: {username, characterName}}">See all
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
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {Character} from '@/store/characters/types/Character.ts'
import CharacterCentric from '@/components/views/character/mixins/CharacterCentric.ts'
import Submission from '@/types/Submission.ts'
import {SingleController} from '@/store/singles/controller.ts'
import RatingRefresh, {useRatingRefresh} from '@/mixins/RatingRefresh.ts'
import {CharacterProps} from '@/types/CharacterProps.ts'
import {useCharacter} from '@/store/characters/hooks.ts'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'

const props = defineProps<CharacterProps>()

const character = useCharacter(props)
const display = useDisplay()

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
    'pb-2': display.smAndDown.value,
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
