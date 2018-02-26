<template>
  <div class="asset-container">
    <div v-if="asset">
      <a :href="asset.file.full" v-if="canDisplay && !textOnly"><img :class="imgClass" :src="asset.file[thumbName]"></a>
      <div v-else-if="!canDisplay">
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
    <div v-if="textOnly" :style="containerStyle">&nbsp;</div>
  </div>
</template>

<script>
  import { RATINGS } from '../lib'
  export default {
    name: 'ac-asset',
    props: {
      'asset': {},
      'imgClass': {},
      'terse': {},
      'thumbName': {},
      'textOnly': {},
      'containerStyle': {
        default: 'min-height: 15rem;'
      },
      'addedTags': {default () { return [] }}
    },
    computed: {
      ratingText () {
        return RATINGS[this.asset.rating]
      },
      tags () {
        return this.asset.tags.concat(this.addedTags)
      },
      blacklisted () {
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
        return this.asset.rating <= this.rating
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
      }
    }
  }
</script>
