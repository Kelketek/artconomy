<template>
  <v-responsive v-if="$vuetify.display.smAndDown || mini" aspect-ratio="1" class="character" :class="{unavailable}">
    <v-card>
      <v-card-text class="pa-2">
        <v-row no-gutters>
          <v-col>
            <v-row no-gutters>
              <v-col cols="8" offset="2">
                <ac-link :to="characterLink">
                  <ac-asset
                      :text="false"
                      :asset="character.primary_submission"
                      thumb-name="thumbnail"
                      :aspect-ratio="1"
                      :allow-preview="false"
                      :alt="characterAltText"
                  />
                </ac-link>
              </v-col>
            </v-row>
            <v-row>
              <v-col class="text-left">
                <ac-link :to="characterLink">
                  {{ character.name }}
                </ac-link>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-responsive>
  <v-card class="character-card" v-else :class="{unavailable}">
    <router-link
        :to="characterLink">
      <ac-asset
          :asset="character.primary_submission"
          thumb-name="thumbnail"
          :terse="true"
          :aspect-ratio="1"
          :allow-preview="false"
          :alt="characterAltText"
      />
    </router-link>
    <v-card-title v-if="showFooter">
      <router-link
          :to="characterLink">
        {{ character.name }}
      </router-link>
    </v-card-title>
  </v-card>
</template>

<style>
.character a {
  text-decoration: none !important;
}
</style>

<script>
import AcAsset from './AcAsset.vue'
import Viewer from '../mixins/viewer.ts'
import AcLink from '@/components/wrappers/AcLink.vue'

export default {
  name: 'ac-character-preview',
  components: {
    AcLink,
    AcAsset,
  },
  mixins: [Viewer],
  computed: {
    characterLink() {
      return {name: 'Character',
        params: {
          username: this.character.user.username,
          characterName: this.character.name,
        },
      }
    },
    characterAltText() {
      if (this.character.primary_submission) {
        const title = this.character.primary_submission.title
        if (!title) {
          return `Untitled Focus Submission for ${this.character.name}`
        }
        return `Focus Submission for ${this.character.name} titled: ${title}`
      }
      return ''
    },
    unavailable() {
      return this.character.hidden
    },
  },
  props: {
    character: {},
    contain: {
      default: false,
    },
    mini: {
      default: false,
    },
    showFooter: {
      default: true,
    },
  },
}
</script>
