<template>
  <div>
    <div v-if="asset.preview">
      <img :src="asset.preview.thumbnail" class="mb-2"/>
    </div>
    <audio controls>
      <source :src="asset.file.full" :type="type">
    </audio>
  </div>
</template>

<script>
  import {getExt} from '../lib'

  export default {
    props: ['asset'],
    name: 'ac-audio-player',
    computed: {
      type () {
        return 'audio/' + getExt(this.asset.file.full).toLowerCase()
      }
    }
  }
</script>