<template>
  <v-card class="asset-card">
    <v-flex>
      <div class="edit-overlay" v-if="editing" v-ripple="{ center: true }" @click="$emit('input', true)">
        <v-container fluid class="pa-0 edit-container">
          <v-layout column justify-content align-center d-flex class="edit-layout">
            <v-flex d-flex>
              <v-layout row wrap align-center justify-content>
                <v-flex text-xs-center class="edit-cta">
                  <slot name="edit-prompt">
                    <v-icon large>photo_camera</v-icon>
                    <p>Edit</p>
                  </slot>
                </v-flex>
              </v-layout>
            </v-flex>
          </v-layout>
        </v-container>
        <div class="backdrop"></div>
      </div>
      <v-img :src="displayImage" :aspect-ratio="ratio" :contain="contain" v-if="renderImage && isImage"
             max-height="90vh" max-width="100%" class="asset-image" ref="imgContainer"
             @click="fullscreen=true"
      ></v-img>
      <v-flex v-else-if="renderImage && !isImage" xs12 text-xs-center>
        <a :href="fullUrl" download><img :src="displayImage" alt="" ref="imgContainer"></a>
      </v-flex>
      <component :asset="asset" :compact="compact" :pop-out="popOut" v-else-if="asset && canDisplay"
                 :is="displayComponent"></component>
      <v-responsive v-else :aspect-ratio="ratio">
        <v-layout column justify-center align-content-center style="height: 100%">
          <v-card-text align-self-center>
            <v-flex text-xs-center>
              <v-icon x-large>block</v-icon>
              <v-flex v-if="text">
                <div v-if="!permittedRating">
                  <p>This piece exceeds your content rating settings.</p>
                  <p v-if="nerfed" class="nerfed-message">Please toggle SFW mode off to see this piece.</p>
                  <p v-else-if="isRegistered && !terse" class="rating-info">
                    This piece is rated '{{ ratingText }}'. <br/>
                    You can change your content rating settings in your
                    <router-link :to="{name: 'Settings', params: {username: viewer.username}}">settings panel.</router-link>
                  </p>
                </div>
                <div v-if="blacklisted.length" class="blacklist-info">
                  <p v-if="terse">This piece contains tags on your blacklist.</p>
                  <p v-else>
                    This piece contains these blacklisted tags:
                    <span v-for="tag in this.blacklisted" :key="tag">{{tag}} </span>
                  </p>
                </div>
              </v-flex>
            </v-flex>
          </v-card-text>
        </v-layout>
      </v-responsive>
      <div class="fullscreen-container" v-if="renderImage && isImage && fullscreen" @click="fullscreen=false">
        <div class="image-container">
          <div class="image-backdrop"><img :src="fullUrl" class="fullscreen-image" alt=""></div>
        </div>
        <div class="backdrop">
        </div>
      </div>
    </v-flex>
    <slot v-if="editing" name="edit-menu">

    </slot>
  </v-card>
</template>

<style lang="sass" scoped>
  .image-backdrop
    background-color: #ffffff
    line-height: 0
  .asset-card
    .edit-overlay
      position: absolute
      width: 100%
      height: 100%
      z-index: 1
      .edit-container, .edit-layout
        height: 100%
      .edit-layout
        position: relative
      .backdrop
        background-color: #000000
        opacity: .40
        width: 100%
        height: 100%
        position: absolute
        top: 0
      .edit-cta
        position: relative
        z-index: 1
  .fullscreen-container
    position: fixed
    top: 0
    left: 0
    height: 100%
    width: 100%
    z-index: 100
    display: flex
    flex-direction: column
    justify-content: center
    .backdrop
      background-color: #000000
      opacity: .90
      width: 100%
      height: 100%
      position: absolute
      top: 0
    .image-container
      text-align: center
      z-index: 101
      position: relative
      display: flex
      flex-direction: row
      justify-content: center
      max-width: 100vw
      max-height: 100vh
      img
        max-width: 100%
        max-height: 100%
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcVideoPlayer from '@/components/AcVideoPlayer.vue'
import AcAudioPlayer from '@/components/AcAudioPlayer.vue'
import AcMarkdownViewer from '@/components/AcMarkdownViewer.vue'
import {COMPONENT_EXTENSIONS, getExt} from '@/lib'
import AssetBase from '@/mixins/asset_base'
import {Asset} from '@/types/Asset'

  @Component({components: {AcVideoPlayer, AcAudioPlayer, AcMarkdownViewer}})
export default class AcAsset extends mixins(AssetBase) {
    @Prop({default: null as unknown as Asset})
    public asset!: Asset
    @Prop({default: 1})
    public aspectRatio!: number|null
    @Prop({required: true})
    public thumbName!: string
    @Prop({required: false})
    public editing!: boolean
    @Prop({default: true})
    public text!: boolean
    public fullscreen = false

    public mounted() {
      window._paq.push(['MediaAnalytics::scanForMedia', this.$el])
    }

    public get displayComponent() {
      if (!this.asset) {
        return null
      }
      const ext = getExt(this.asset.file.full)
      if (['gallery', 'full', 'preview'].indexOf(this.thumbName) === -1) {
        return null
      }
      // @ts-ignore
      return COMPONENT_EXTENSIONS[ext]
    }
    public get renderImage() {
      return this.canDisplay && (this.isImage || !this.displayComponent)
    }
    public get ratio() {
      if ((!this.canDisplay) && (this.aspectRatio === null)) {
        return 1
      }
      return this.aspectRatio
    }
    public get fullUrl() {
      if (this.asset === null) {
        return this.fallbackImage
      }
      return this.asset.file.full
    }
}
</script>
