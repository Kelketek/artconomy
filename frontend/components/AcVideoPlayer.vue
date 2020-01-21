<template>
  <v-row no-gutters  >
    <v-col class="text-center" cols="12" ><video controls :width="width" style="max-width: 100%">
        <source :src="asset.file.full" :type="type">
      </video>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import {getExt} from '@/lib/lib'
import Component from 'vue-class-component'
import Vue from 'vue'
import {Prop} from 'vue-property-decorator'
import {Asset} from '@/types/Asset'

const VID_TYPES = {
  MP4: 'video/mp4',
  OGV: 'video/ogg',
  WEBM: 'video/webm',
}
  @Component
export default class AcVideoPlayer extends Vue {
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
</script>
