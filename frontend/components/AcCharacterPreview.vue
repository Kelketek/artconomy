<template>
  <v-responsive
    v-if="smAndDown || mini"
    aspect-ratio="1"
    class="character"
    :class="{unavailable}"
  >
    <v-card>
      <v-card-text class="pa-2">
        <v-row no-gutters>
          <v-col>
            <v-row no-gutters>
              <v-col
                cols="8"
                offset="2"
              >
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
  <v-card
    v-else
    class="character-card"
    :class="{unavailable}"
  >
    <router-link
      :to="characterLink"
    >
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
        :to="characterLink"
      >
        {{ character.name }}
      </router-link>
    </v-card-title>
  </v-card>
</template>

<script setup lang="ts">
import AcAsset from './AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'
import {Character} from '@/store/characters/types/main'

const {smAndDown} = useDisplay()

declare interface AcCharacterPreviewProps {
  character: Character,
  mini?: boolean,
  showFooter?: boolean,
}

const props = withDefaults(defineProps<AcCharacterPreviewProps>(), {showFooter: true, mini: false})
const characterLink = computed(() => ({
  name: 'Character',
  params: {username: props.character.user.username, characterName: props.character.name},
}))
const characterAltText = computed(() => {
  if (props.character.primary_submission) {
    const title = props.character.primary_submission.title
    if (!title) {
      return `Untitled Focus Submission for ${props.character.name}`
    }
    return `Focus Submission for ${props.character.name} titled: ${title}`
  }
  return ''
})
const unavailable = computed(() => props.character.private)
</script>

<style>
.character a {
  text-decoration: none !important;
}
</style>
