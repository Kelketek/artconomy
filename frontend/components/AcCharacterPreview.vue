<template>
  <v-card class="character-card">
    <router-link
        :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
        <ac-asset
            :asset="character.primary_submission"
            thumb-name="thumbnail"
            :terse="true"
            :aspect-ratio="1"
        />
    </router-link>
    <v-card-title>
      <router-link
          :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
        {{ character.name }}
      </router-link>
    </v-card-title>
  </v-card>
</template>

<script>
import AcAsset from './AcAsset'
import Viewer from '../mixins/viewer'
import {artCall} from '../lib'

export default {
  name: 'ac-character-preview',
  components: {
    AcAsset,
  },
  mixins: [Viewer],
  props: {
    character: {},
    contain: {
      default: false,
    },
  },
}
</script>
