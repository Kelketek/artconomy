<template>
  <v-row
    no-gutters
    class="ac-audio-player"
  >
    <v-col
      v-if="asset.preview"
      cols="12"
      sm="6"
      offset-sm="3"
      md="4"
      offset-md="4"
    >
      <v-img
        :src="asset.preview.thumbnail"
        class="mb-2"
        :aspect-ratio="1"
        alt="alt"
      />
    </v-col>
    <v-col
      class="text-center"
      cols="12"
    >
      <audio controls>
        <source
          :src="asset.file!.full"
          :type="type"
        >
      </audio>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {getExt} from '@/mixins/asset_base.ts'
import {computed} from 'vue'
import type {Asset} from '@/types/main'

const props = defineProps<{asset: Asset, alt: string}>()
const type = computed(() =>  'audio/' + getExt(props.asset.file!.full).toLowerCase())
</script>
