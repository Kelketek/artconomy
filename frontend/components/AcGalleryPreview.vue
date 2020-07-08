<template>
  <v-responsive v-if="($vuetify.breakpoint.smAndDown && showFooter) || mini" aspect-ratio="1" class="submission" :class="{unavailable}">
    <v-card>
      <v-card-text class="pa-2">
        <v-row no-gutters>
          <v-col cols="8" offset="2">
            <ac-link :to="submissionLink">
              <ac-asset :text="false" :asset="submission" thumb-name="thumbnail" />
            </ac-link>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
              <ac-link :to="submissionLink">
                <v-row no-gutters  >
                  <v-col>
                    <div class="text-left" >{{ submission.title }}</div>
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
        :aspect-ratio="aspectRatio"
      />
    </ac-link>
    <ac-link :to="submissionLink" v-if="showFooter">
      <v-card-text class="pa-1">
        <v-row dense>
          <v-col class="text-left" ><strong>{{ submission.title }}</strong></v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <v-row no-gutters class="submission-stats">
              <v-col class="text-left" >
                <v-icon>favorite</v-icon>&nbsp;
                <span>{{ submission.favorite_count }}</span>&nbsp;
                <v-icon>comment</v-icon>&nbsp;
                <span>{{ submission.comment_count }}</span>&nbsp;
              </v-col>
              <slot name="stats-append"><v-spacer /></slot>
            </v-row>
          </v-col>
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
