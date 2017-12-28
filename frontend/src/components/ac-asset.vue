<template>
  <div class="asset-container">
    <a :href="asset.file.full" v-if="asset.rating <= rating"><img :class="imgClass" :src="asset.file[thumbName]"></a>
    <div v-else>
      <div class="text-center" v-if="!terse">
        <i class="fa fa-ban fa-5x mt-4 mb-4"></i>
        <p>This piece exceeds your current content rating settings.</p>
        <p v-if="viewer.rating && (asset.rating <= viewer.rating)">Please toggle SFW mode off to see this piece.</p>
        <p v-else-if="viewer.username === undefined">Registered users can customize their content rating settings.</p>
        <p v-else>
          This piece is rated '{{ ratingText }}'. <br />
          You can change your content rating settings in the <router-link :to="{name: 'Settings', params: {username: viewer.username}}">settings panel.</router-link>
        </p>
      </div>
      <div v-else class="text-center terse-container" :class="imgClass">
        <i class="fa fa-ban fa-5x mb-3 mt-3"></i>
        <p>This piece exceeds your current content rating settings.</p>
      </div>
    </div>
  </div>
</template>

<style>
  .asset-container {
    display: inline-block;
    vertical-align: middle;
  }
</style>

<script>
  import Viewer from '../mixins/viewer'
  import { RATINGS } from '../lib'
  export default {
    mixins: [Viewer],
    props: ['asset', 'imgClass', 'terse', 'thumbName'],
    computed: {
      ratingText () {
        return RATINGS[this.asset.rating]
      }
    }
  }
</script>
