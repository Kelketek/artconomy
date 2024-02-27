<template>
  <v-responsive v-if="($vuetify.display.smAndDown && showFooter) || mini" aspect-ratio="1" class="submission"
                :class="{unavailable}">
    <v-card>
      <v-card-text class="pa-2">
        <v-row no-gutters>
          <v-col cols="8" offset="2">
            <ac-link :to="submissionLink">
              <ac-asset :text="false" :asset="submission" thumb-name="thumbnail" :allow-preview="false"
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
          :alt="showFooter ? '' : submission.title || 'Untitled Submission.'"
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

<script>
import AcAsset from './AcAsset.vue'
import Viewer from '../mixins/viewer.ts'
import AcLink from '@/components/wrappers/AcLink.vue'

export default {
  components: {
    AcLink,
    AcAsset,
  },
  name: 'ac-gallery-preview',
  mixins: [Viewer],
  props: {
    submission: {},
    thumbName: {
      default: 'thumbnail',
    },
    compact: {
      default: false,
    },
    contain: {
      default: false,
    },
    showFooter: {
      default: true,
    },
    aspectRatio: {
      default: 1,
    },
    mini: {
      default: false,
    },
    text: {
      default: true,
    },
    linked: {
      default: true,
    },
    allowPreview: {
      default: false,
    },
    forceHidden: {
      default: false,
    },
  },
  computed: {
    submissionLink() {
      if (!this.linked) {
        return null
      }
      return {
        name: 'Submission',
        params: {submissionId: this.submission.id},
      }
    },
    unavailable() {
      return this.submission.private || this.forceHidden
    },
  },
}
</script>
