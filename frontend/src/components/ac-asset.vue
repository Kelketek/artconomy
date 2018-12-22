<template>
  <div class="asset-container">
    <div v-if="asset">
      <div v-if="canDisplay && !textOnly">
        <div v-if="isImage">
          <img :class="imgClass" :src="displayImage" @click="fullscreen = true">
        </div>
        <div v-else-if="displayComponent">
          <component :asset="asset" :imgClass="imgClass" :compact="compact" :is="displayComponent"></component>
        </div>
        <div v-else>
          <a :href="asset.file.full" download>
            <img :class="imgClass" :src="displayImage">
          </a>
        </div>
        <div v-if="fullscreen" class="fullscreen-container" @click="fullscreen=false">
          <img :class="imgClass" :src="asset.file.full" v-if="canDisplay && !textOnly">
        </div>
      </div>
      <div v-else-if="!canDisplay" :style="style" class="text-xs-center">
        <div style="min-height: 20%;">&nbsp;</div>
        <div class="text-xs-center" v-if="!terse">
          <v-icon x-large>block</v-icon>
          <div v-if="!permittedRating">
            <p>This piece exceeds your current content rating settings.</p>
            <p v-if="viewer.rating && (asset.rating <= viewer.rating)">Please toggle SFW mode off to see this piece.</p>
            <p v-else-if="viewer.username === undefined">Registered users can customize their content rating settings.</p>
            <p v-else>
              This piece is rated '{{ ratingText }}'. <br />
              You can change your content rating settings in the <router-link :to="{name: 'Settings', params: {username: viewer.username}}">settings panel.</router-link>
            </p>
          </div>
          <div v-if="blacklisted.length" class="p-2">
            This piece contains these blacklisted tags:
            <span v-for="tag in this.blacklisted" :key="tag">{{tag}} </span>
          </div>
        </div>
        <div v-else class="text-xs-center terse-container" :class="imgClass">
          <v-icon x-large>block</v-icon>
          <p v-if="!permittedRating">This piece exceeds your current content rating settings.</p>
          <p v-if="blacklisted.length">This piece contains tags on your blacklist.</p>
        </div>
      </div>
    </div>
    <div v-else-if="!asset && !textOnly">
      <img :class="defaultClass" src="/static/images/default-avatar.png" />
    </div>
    <div v-if="textOnly && canDisplay" :style="containerStyle">&nbsp;</div>
  </div>
</template>

<style scoped>
  .fullscreen-container {
    position: fixed;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 100;
    background-color: #303030;
  }
  .fullscreen-container img {
    max-height: 100%;
    max-width: 100%;
  }
</style>

<script>
  import {COMPONENT_EXTENSIONS, extPreview, getExt, RATINGS} from '../lib'
  import AcVideoPlayer from './ac-video-player'
  import AcSvgViewer from './ac-svg-viewer'
  import AcMarkdownViewer from './ac-markdown-viewer'
  import AcAudioPlayer from './ac-audio-player'
  import AcDangerFile from './ac-danger-file'
  export default {
    name: 'ac-asset',
    props: {
      'asset': {},
      'imgClass': {},
      'terse': {},
      'thumbName': {},
      'textOnly': {},
      'compact': {},
      'containerStyle': {
        default: 'min-height: 15rem;'
      },
      'addedTags': {default () { return [] }}
    },
    components: {AcDangerFile, AcAudioPlayer, AcMarkdownViewer, AcSvgViewer, AcVideoPlayer},
    data () {
      return {
        fullscreen: false
      }
    },
    computed: {
      ratingText () {
        return RATINGS[this.asset.rating]
      },
      tags () {
        return this.asset.tags.concat(this.addedTags)
      },
      displayImage () {
        if (['gallery', 'full', 'preview'].indexOf(this.thumbName) === -1) {
          if (this.asset.preview) {
            return this.asset.preview.thumbnail
          }
        }
        if (!this.isImage) {
          return extPreview(this.asset.file.full)
        }
        return this.asset.file[this.thumbName]
      },
      displayComponent () {
        let ext = getExt(this.asset.file.full)
        // Special case-- SVGs are natively supported but the backend can't thumbnail them.
        if (ext === 'SVG') {
          return 'ac-svg-viewer'
        }
        if (['gallery', 'full', 'preview'].indexOf(this.thumbName) === -1) {
          return null
        }
        return COMPONENT_EXTENSIONS[ext]
      },
      blacklisted () {
        if (!this.asset) {
          return false
        }
        let blacklist = this.viewer.blacklist
        if (blacklist === undefined) {
          blacklist = []
        }
        if (this.asset.tags === undefined) {
          return []
        }
        return this.tags.filter((n) => this.viewer.blacklist.includes(n))
      },
      permittedRating () {
        if (!this.asset) {
          return true
        }
        return this.asset.rating <= this.rating
      },
      isImage () {
        return (this.asset.file['__type__'] === 'data:image')
      },
      canDisplay () {
        if (this.permittedRating) {
          if (!this.blacklisted.length) {
            return true
          }
        }
      },
      defaultClass () {
        let classes = {}
        classes['asset-' + this.thumbName] = true
        classes[this.imgClass] = true
        return classes
      },
      style () {
        if (!this.containerStyle) {
          return {
            default: 'min-height: 15rem;'
          }
        } else {
          return this.containerStyle
        }
      }
    }
  }
</script>
