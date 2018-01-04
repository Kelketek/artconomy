<template>
  <div class="container">
    <ac-asset-gallery :endpoint="`/api/profiles/v1/${this.username}/characters/${this.characterName}/assets/`" :limit="4" />
  </div>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'

  export default {
    props: ['username', 'characterName'],
    components: {AcAssetGallery},
    name: 'CharacterGallery'
  }
</script>

<style scoped>

</style>