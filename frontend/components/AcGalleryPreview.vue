<template>
  <v-responsive v-if="(smAndDown && showFooter) || mini" aspect-ratio="1" class="submission"
                :class="{unavailable}">
    <v-card>
      <v-card-text class="pa-2">
        <v-row no-gutters>
          <v-col cols="8" offset="2">
            <ac-link :to="submissionLink">
              <ac-asset :text="false" :asset="submission" thumb-name="thumbnail" :allow-preview="false"
                        :alt="altText"
                        :aspect-ratio="1"
                        :class="{fade: unavailable}"/>
            </ac-link>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <ac-link :to="submissionLink">
              <v-row no-gutters>
                <v-col>
                  <div class="text-left">{{ submission.title }}</div>
                </v-col>
              </v-row>
            </ac-link>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-responsive>
  <v-card class="submission" v-else :class="{unavailable}">
    <ac-link :to="submissionLink">
      <ac-asset
          :asset="submission"
          :thumb-name="thumbName"
          :contain="contain"
          :compact="compact"
          :text="text"
          :terse="true"
          :aspect-ratio="aspectRatio"
          :allow-preview="allowPreview"
          :alt="showFooter ? '' : altText"
      />
    </ac-link>
    <ac-link :to="submissionLink" v-if="showFooter">
      <v-card-text class="pa-1" v-if="submission.title">
        <v-row dense>
          <v-col class="text-left"><strong>{{ submission.title }}</strong></v-col>
        </v-row>
      </v-card-text>
    </ac-link>
  </v-card>
</template>

<style>
.gallery-preview-media .v-card__media__content {
  justify-content: center;
}

.submission a {
  text-decoration: none !important;
}
</style>

<style scoped>
.unavailable {
  opacity: .5;
}
</style>

<script setup lang="ts">
import AcAsset from './AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Submission from '@/types/Submission.ts'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'

declare interface AcGalleryPreviewProps {
  submission: Submission,
  thumbName?: string,
  compact?: boolean,
  contain?: boolean,
  showFooter?: boolean,
  aspectRatio?: number|null,
  mini?: boolean,
  text?: boolean,
  linked?: boolean,
  allowPreview?: boolean,
  forceHidden?: boolean,
}

const props = withDefaults(defineProps<AcGalleryPreviewProps>(), {
  thumbName: 'thumbnail',
  compact: false,
  contain: false,
  showFooter: true,
  aspectRatio: 1,
  mini: false,
  text: true,
  linked: true,
  allowPreview: false,
  forceHidden: false,
})

const {smAndDown} = useDisplay()

const submissionLink = computed(() => {
  if (!props.linked) {
    return null
  }
  return {
    name: 'Submission',
    params: {submissionId: props.submission.id}
  }
})
const altText = computed(() => props.submission.title || 'Untitled Submission.')
const unavailable = computed(() => props.submission.private || props.forceHidden)
</script>
