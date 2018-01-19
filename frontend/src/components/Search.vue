<template>
  <div>
    <div class="container">
      <b-tabs>
        <b-tab title="Submissions">
          <div v-if="query.q.length === 0" class="text-center pt-2">
            <p>Enter tags to search for in the search bar above</p>
          </div>
          <ac-asset-gallery ref="assetSearch" class="pt-2" endpoint="/api/profiles/v1/search/assets/" :query-data="query" />
        </b-tab>
      </b-tabs>
    </div>
  </div>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'
  import { paramHandleMap } from '../lib'

  let TabMap = {
    submissions: 0
  }

  export default {
    components: {AcAssetGallery},
    name: 'search',
    methods: {
      emptyResult (ref) {
        return ref && (ref.growing !== null) && (ref.growing.length === 0)
      }
    },
    computed: {
      query: {
        get () {
          return {q: this.$route.query['q'] || []}
        }
      },
      tab: paramHandleMap('tabName', TabMap, ['subTabName'])
    }
  }
</script>

<style scoped>

</style>