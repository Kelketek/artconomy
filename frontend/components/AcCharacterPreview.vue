<template>
  <v-responsive v-if="$vuetify.breakpoint.smAndDown || mini" aspect-ratio="1" class="submission">
    <v-card>
      <v-layout column class="pt-2">
        <v-layout row wrap>
          <v-flex xs8 offset-xs2>
            <ac-link :to="characterLink">
              <ac-asset :text="false" :asset="character.primary_submission" thumb-name="thumbnail"></ac-asset>
            </ac-link>
          </v-flex>
        </v-layout>
        <v-flex>
          <v-card-text class="pb-2">
            <ac-link :to="characterLink">
              <v-layout row wrap>
                <v-layout column>
                  <v-flex text-xs-left>{{ character.name }}</v-flex>
                </v-layout>
              </v-layout>
            </ac-link>
          </v-card-text>
        </v-flex>
      </v-layout>
    </v-card>
  </v-responsive>
  <v-card class="character-card" v-else>
    <router-link
        :to="characterLink">
        <ac-asset
            :asset="character.primary_submission"
            thumb-name="thumbnail"
            :terse="true"
            :aspect-ratio="1"
        />
    </router-link>
    <v-card-title>
      <router-link
          :to="characterLink">
        {{ character.name }}
      </router-link>
    </v-card-title>
  </v-card>
</template>

<script>
import AcAsset from './AcAsset'
import Viewer from '../mixins/viewer'
import {artCall} from '../lib'
import AcLink from '@/components/wrappers/AcLink'

export default {
  name: 'ac-character-preview',
  components: {
    AcLink,
    AcAsset,
  },
  mixins: [Viewer],
  computed: {
    characterLink() {
      return {name: 'Character', params: {username: this.character.user.username, characterName: this.character.name}}
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
  },
}
</script>
