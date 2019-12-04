<template>
  <v-responsive v-if="($vuetify.breakpoint.smAndDown && showFooter) || mini" aspect-ratio="1" class="submission" :class="{unavailable}">
    <v-card>
      <v-layout column class="pt-2">
        <v-layout row wrap>
          <v-flex xs8 offset-xs2>
            <ac-link :to="submissionLink">
              <ac-asset :text="false" :asset="submission" thumb-name="thumbnail"></ac-asset>
            </ac-link>
          </v-flex>
        </v-layout>
        <v-flex>
          <v-card-text class="pb-2">
            <ac-link :to="submissionLink">
              <v-layout row wrap>
                <v-layout column>
                  <v-flex text-xs-left>{{ submission.title }}</v-flex>
                  <v-flex>
                    <v-layout row>
                      <v-flex text-xs-left>
                        <v-icon small>favorite</v-icon>
                        {{ submission.favorite_count }}
                        <v-icon small>comment</v-icon>
                        {{ submission.comment_count }}
                      </v-flex>
                      <slot name="stats-append"></slot>
                    </v-layout>
                  </v-flex>
                </v-layout>
              </v-layout>
            </ac-link>
          </v-card-text>
        </v-flex>
      </v-layout>
    </v-card>
  </v-responsive>
  <v-flex class="submission" v-else :class="{unavailable}">
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
              <v-layout row class="submission-stats">
                <v-flex text-xs-left>
                  <v-icon>favorite</v-icon>
                  <span>{{ submission.favorite_count }}</span>
                  <v-icon>comment</v-icon>
                  <span>{{ submission.comment_count }}</span>
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
    text-decoration: none !important;
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
    mini: {
      default: false,
    },
  },
  computed: {
    submissionLink() {
      return {name: 'Submission', params: {submissionId: this.submission.id}}
    },
    unavailable() {
      return this.submission.private
    },
  },
}
</script>
