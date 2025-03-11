<template>
  <v-row
    no-gutters
    class="ac-video-player"
  >
    <v-col
      class="text-center"
      cols="12"
    >
      <video
        controls
        :width="width"
        style="max-width: 100%"
      >
        <source
          :src="asset.file!.full"
          :type="type"
        >
      </video>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">

import {getExt} from '@/mixins/asset_base.ts'
import {computed} from 'vue'
import type {Asset} from '@/types/main'

const VID_TYPES = {
  MP4: 'video/mp4',
  OGV: 'video/ogg',
  WEBM: 'video/webm',
}

const props = defineProps<{asset: Asset}>()
// @ts-expect-error Explicitly handling undefined fallthrough.
const type = computed(() => VID_TYPES[getExt(props.asset.file!.full)] || 'type/unknown')
const width = 800
</script>
