<template>
  <v-layout row wrap>
    <v-flex xs12 sm6 offset-sm3 md4 offset-md4 v-if="asset.preview">
      <v-img :src="asset.preview.thumbnail" class="mb-2" :aspect-ratio="1"/>
    </v-flex>
    <v-flex xs12 text-xs-center>
      <audio controls>
        <source :src="asset.file.full" :type="type">
      </audio>
    </v-flex>
  </v-layout>
</template>

<script>
import {getExt} from '../lib'

export default {
  props: ['asset'],
  name: 'ac-audio-player',
  computed: {
    type() {
      return 'audio/' + getExt(this.asset.file.full).toLowerCase()
    },
  },
}
</script>
