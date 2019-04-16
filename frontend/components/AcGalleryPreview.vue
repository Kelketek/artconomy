<template>
  <v-flex class="submission">
    <v-card>
      <ac-link :to="submissionLink">
        <ac-asset
            :asset="submission"
            :thumb-name="thumbName"
            :contain="contain"
            :compact="compact"
            :aspect-ratio="aspectRatio"
        />
      </ac-link>
      <ac-link :to="submissionLink" v-if="showFooter">
        <v-flex pa-2>
          <v-layout column>
            <v-flex text-xs-left>{{ submission.title }}</v-flex>
            <v-flex>
              <v-layout row>
                <v-flex text-xs-left>
                  <v-icon>favorite</v-icon>
                  {{ submission.favorite_count }}
                  <v-icon>comment</v-icon>
                  {{ submission.comment_count }}
                </v-flex>
                <slot name="stats-append"></slot>
              </v-layout>
            </v-flex>
          </v-layout>
        </v-flex>
      </ac-link>
    </v-card>
  </v-flex>
</template>

<style>
  .gallery-preview-media .v-card__media__content {
    justify-content: center;
  }
  .submission a {
    text-decoration: none;
  }
</style>

<script>
import AcAsset from './AcAsset'
import Viewer from '../mixins/viewer'
import AcLink from '@/components/wrappers/AcLink'

export default {
  components: {AcLink, AcAsset},
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
  },
  computed: {
    submissionLink() {
      return {name: 'Submission', params: {submissionId: this.submission.id}}
    },
  },
}
</script>
