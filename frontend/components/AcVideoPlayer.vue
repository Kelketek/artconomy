<template>
  <v-row no-gutters>
    <v-col class="text-center" cols="12">
      <video controls :width="width" style="max-width: 100%">
        <source :src="asset.file.full" :type="type">
      </video>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {getExt} from '@/lib/lib.ts'
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {Asset} from '@/types/Asset.ts'

const VID_TYPES = {
  MP4: 'video/mp4',
  OGV: 'video/ogg',
  WEBM: 'video/webm',
}

@Component
class AcVideoPlayer extends Vue {
  @Prop()
  public asset!: Asset

  public get type() {
    // @ts-ignore
    return VID_TYPES[getExt(this.asset.file.full)] || 'type/unknown'
  }

  public get width() {
    return 800
  }
}

export default toNative(AcVideoPlayer)
</script>
