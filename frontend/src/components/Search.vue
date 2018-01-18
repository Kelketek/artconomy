<template>
  <div>
    <div class="container">
      <ac-asset-gallery endpoint="/api/profiles/v1/search/assets/" :query-data="query" />
    </div>
  </div>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'

  export default {
    components: {AcAssetGallery},
    name: 'search',
    computed: {
      query: {
        get () {
          return {q: this.$route.query['q'] || ''}
        }
      }
    }
  }
</script>

<style scoped>

</style>