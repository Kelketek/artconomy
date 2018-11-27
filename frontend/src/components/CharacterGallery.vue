<template>
  <div class="container">
    <ac-asset-gallery :endpoint="`/api/profiles/v1/account/${this.username}/characters/${this.characterName}/assets/`" :limit="20" />
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