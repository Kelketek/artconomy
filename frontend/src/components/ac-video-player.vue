<template>
  <div>
    <video controls :width="width">
      <source :src="asset.file.full" :type="type">
    </video>
  </div>
</template>

<script>
  import {getExt} from '../lib'

  const VID_TYPES = {
    'MP4': 'video/mp4',
    'OGV': 'video/ogg',
    'WEBM': 'video/webm'
  }
  export default {
    name: 'ac-video-player',
    props: ['asset'],
    computed: {
      type () {
        return VID_TYPES[getExt(this.asset.file.full)] || 'type/unknown'
      },
      width () {
        return 800
      }
    }
  }
</script>