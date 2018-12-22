<template>
  <div>
    <img :class="imgClass" :src="asset.file.full" @click="fullscreen = true">
    <div v-if="fullscreen" class="fullscreen-container" @click="fullscreen=false">
      <img :class="imgClass" :src="asset.file.full" v-if="canDisplay && !textOnly">
    </div>
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
   export default {
     name: 'ac-svg-viewer',
     props: ['asset', 'imgClass'],

   }
</script>