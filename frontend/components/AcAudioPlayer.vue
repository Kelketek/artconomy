<template>
  <v-row no-gutters  >
    <v-col cols="12" sm="6" offset-sm="3" md="4" offset-md="4" v-if="asset.preview">
      <v-img :src="asset.preview.thumbnail" class="mb-2" :aspect-ratio="1"/>
    </v-col>
    <v-col class="text-center" cols="12" >
      <audio controls>
        <source :src="asset.file.full" :type="type">
      </audio>
    </v-col>
  </v-row>
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
