<template>
  <div class="asset-container">
    <a :href="asset.file" v-if="asset.rating <= rating"><img :src="asset.file"></a>
    <div v-else class="text-center">
      <div><i class="fa fa-ban fa-5x mt-4 mb-4"></i></div>
      <p>This piece exceeds your current content rating settings.</p>
      <p v-if="viewer.rating && (asset.rating <= viewer.rating)">Please toggle SFW mode off to see this piece.</p>
      <p v-else-if="viewer.username === undefined">Registered users can customize their content rating settings.</p>
      <p v-else>You can change your content rating settings in the <router-link :to="{name: 'Settings', params: {username: viewer.username}}">settings panel.</router-link></p>
    </div>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  export default {
    mixins: [Viewer],
    props: ['asset']
  }
</script>

<style scoped>
</style>