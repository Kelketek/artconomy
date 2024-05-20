<template>
  <v-card class="asset-card" ref="el">
    <v-row no-gutters>
      <div class="edit-overlay" v-if="editing" v-ripple="{ center: true }" @click="emit('update:modelValue', true)">
        <v-container fluid class="pa-0 edit-container">
          <v-row no-gutters class="edit-layout justify-content d-flex">
            <v-col class="d-flex">
              <v-row no-gutters class="justify-content" align="center">
                <v-col class="edit-cta text-center">
                  <slot name="edit-prompt">
                    <v-icon large :icon="mdiPencil"/>
                    <p>Edit</p>
                  </slot>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-container>
        <div class="backdrop"></div>
      </div>
      <v-col cols="12" v-if="renderImage && isImage" class="d-flex justify-center">
        <v-img :src="displayImage" :aspect-ratio="ratio || undefined" :contain="contain"
               :max-height="maxHeight" :max-width="maxWidth" class="asset-image align-center"
               itemprop="image" :alt="alt" :eager="immediate"
               :transition="immediate ? false : transition"
               ref="imageContainer"
        />
      </v-col>
      <v-col class="text-center icon-image" v-else-if="renderImage && !isImage" cols="12">
        <img :src="displayImage" :alt="alt" ref="imgContainer">
      </v-col>
      <v-col cols="12" v-else-if="asset && canDisplay">
        <component :asset="asset" :compact="compact" :pop-out="popOut"
                   :is="displayComponent" :alt="alt"/>
      </v-col>
      <v-col cols="12" v-else>
        <v-responsive :aspect-ratio="ratio || undefined">
          <v-row no-gutters justify="center" align-content="center" style="height: 100%">
            <v-col>
              <v-card-text align-self-center>
                <v-row no-gutters>
                  <v-col class="text-center" cols="12">
                    <v-icon x-large :icon="mdiCancel"/>
                    <v-col v-if="text">
                      <div v-if="!permittedRating">
                        <div>This piece exceeds your content rating settings.</div>
                        <p v-if="nerfed && !terse" class="nerfed-message">Please toggle SFW mode off to see this piece.</p>
                        <p v-else-if="isRegistered && !terse" class="rating-info">
                          This piece is rated '{{ ratingText }}'. <br/>
                          <v-btn @click="ageCheck({force: true, value: asset!.rating})" class="mt-2" color="primary"
                                 variant="elevated">Adjust
                            my Settings
                          </v-btn>
                        </p>
                        <p v-else-if="!terse">
                          This piece is rated '{{ ratingText }}'. <br/>
                          <v-btn @click="ageCheck({force: true, value: asset!.rating})" color="primary" class="mt-2"
                                 variant="flat">
                            Adjust my Settings
                          </v-btn>
                        </p>
                      </div>
                      <div v-if="blacklisted.length" class="blacklist-info">
                        <p v-if="terse">This piece contains tags you've blocked.</p>
                        <p v-else>
                          This piece contains these blocked tags:
                          <span v-for="tag in blacklisted" :key="tag">{{ tag }} </span>
                        </p>
                      </div>
                      <div v-if="nsfwBlacklisted.length" class="nsfw-blacklist-info">
                        <p v-if="terse">This piece contains tags you've blocked in an NSFW context.</p>
                        <p v-else>
                          This piece contains these blocked tags:
                          <span v-for="tag in nsfwBlacklisted" :key="tag">{{ tag }} </span>
                        </p>
                      </div>
                    </v-col>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-col>
          </v-row>
        </v-responsive>
      </v-col>
    </v-row>
    <slot v-if="editing" name="edit-menu">

    </slot>
  </v-card>
</template>

<style scoped>
.asset-card .edit-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.asset-card .edit-overlay .edit-container, .asset-card .edit-overlay .edit-layout {
  height: 100%;
}

.asset-card .edit-overlay .edit-layout {
  position: relative;
}

.asset-card .edit-overlay .backdrop {
  background-color: #000000;
  opacity: .60;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
}

.asset-card .edit-overlay .edit-cta {
  position: relative;
  z-index: 1;
}


</style>

<script setup lang="ts">
import {assetDefaults, getExt, useAssetHelpers} from '@/mixins/asset_base.ts'
import {Asset} from '@/types/Asset.ts'
import AssetProps from '@/types/AssetProps.ts'
import {computed, defineAsyncComponent, onMounted, ref} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {usePrerendering} from '@/mixins/prerendering.ts'
import {mdiCancel, mdiPencil} from '@mdi/js'
import {VImg} from 'vuetify/components'
import {useDisplay} from 'vuetify'

const AcVideoPlayer = defineAsyncComponent(() => import('@/components/AcVideoPlayer.vue'))
const AcMarkdownViewer = defineAsyncComponent(() => import('@/components/AcMarkdownViewer.vue'))
const AcAudioPlayer = defineAsyncComponent(() => import('@/components/AcAudioPlayer.vue'))
// const AcPdfViewer = defineAsyncComponent(() => import('@/components/AcPdfViewer.vue'))
const COMPONENT_EXTENSIONS = {
  MP4: AcVideoPlayer,
  WEBM: AcVideoPlayer,
  OGV: AcVideoPlayer,
  TXT: AcMarkdownViewer,
  MD: AcMarkdownViewer,
  MP3: AcAudioPlayer,
  WAV: AcAudioPlayer,
  OGG: AcAudioPlayer,
  // PDF: AcPdfViewer,
}

declare interface AcAssetProps extends AssetProps {
  asset?: Asset | null,
  aspectRatio?: number | null
  thumbName: string,
  editing?: boolean,
  text?: boolean,
  eager?: boolean,
  transition?: false|string,
}

const props = withDefaults(defineProps<AcAssetProps>(), {
  ...assetDefaults(),
  asset: null,
  aspectRatio: 1,
  text: true,
  eager: false,
})

const {ageCheck, isRegistered} = useViewer()

const {
  isImage,
  displayImage,
  ratingText,
  blacklisted,
  nsfwBlacklisted,
  permittedRating,
  nerfed,
  canDisplay,
} = useAssetHelpers(props)

const imageContainer = ref<null|typeof VImg>(null)

const el = ref<HTMLElement | null>(null)

onMounted(() => window._paq.push(['MediaAnalytics::scanForMedia', el.value]))

const emit = defineEmits<{'update:modelValue': [value: boolean]}>()

const displayComponent = computed(() => {
  if (!props.asset) {
    return null
  }
  const ext = getExt(props.asset.file.full)
  if (['gallery', 'full', 'preview'].indexOf(props.thumbName) === -1) {
    return null
  }
  // @ts-ignore
  return COMPONENT_EXTENSIONS[ext]
})

const renderImage = computed(() => canDisplay.value && (isImage.value || !displayComponent.value))

const {prerendering} = usePrerendering()

const immediate = computed(() => prerendering.value || props.eager)

const ratio = computed(() => {
  if ((!canDisplay.value) && (props.aspectRatio === null)) {
    return 1
  }
  return props.aspectRatio
})

const display = useDisplay()

const maxHeight = computed(() => {
  const defaultHeight = '90vh'
  if (!displayImage.value || props.thumbName === 'thumbnail') {
    return defaultHeight
  }
  return Math.min(imageContainer.value?.naturalHeight || defaultHeight, .9 * display.height.value)
})
const maxWidth = computed(() => {
  const defaultWidth = '100%'
  if (!displayImage.value || props.thumbName === 'thumbnail') {
    return defaultWidth
  }
  return imageContainer.value?.naturalWidth || defaultWidth
})
</script>
