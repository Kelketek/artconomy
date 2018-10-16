<template>
  <v-container v-if="response" grid-list-md>
    <slot name="header" v-if="show && header" />
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="error">
        <p>{{error}}</p>
      </v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" />
      </v-flex>
      <v-flex xs12 sm4 lg3 v-for="(transfer, key, index) in results" :key="key">
        <v-card>
          <router-link :to="{name: 'CharacterTransfer', params: {username: username, transferID: transfer.id}}">
            <v-img
                :contain="false"
                :src="$img(transfer.character && transfer.character.primary_asset, 'thumbnail')"
            >
              <ac-asset
                  :asset="transfer.character && transfer.character.primary_asset"
                  thumb-name="thumbnail"
                  :terse="true"
                  :text-only="true"
              />
            </v-img>
          </router-link>
          <v-card-title>
            <router-link :to="{name: 'CharacterTransfer', params: {username: username, transferID: transfer.id}}">
              {{ (transfer.character && transfer.character.name) || transfer.saved_name }}
            </router-link>
          </v-card-title>
        </v-card>
      </v-flex>
      <v-flex xs12 text-xs-center v-if="show">
        <v-pagination v-model="currentPage" :length="totalPages" v-if="totalPages > 1 && !noPagination" />
      </v-flex>
      <v-flex v-if="noPagination && to && currentPage !== totalPages" xs12 text-xs-center>
        <v-btn color="primary" :to="to">{{seeMoreText}}</v-btn>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcGalleryPreview from './ac-gallery-preview'
  import AcCharacterPreview from './ac-character-preview'
  import AcAssetGallery from './ac-asset-gallery'
  import AcAsset from './ac-asset'
  export default {
    props: ['endpoint', 'header', 'noPagination', 'to', 'seeMoreText', 'username'],
    components: {AcAsset, AcAssetGallery, AcCharacterPreview, AcGalleryPreview},
    data () {
      return {
        url: this.endpoint
      }
    },
    created () {
      this.fetchItems()
    },
    watch: {
      rating () {
        this.fetchItems()
      }
    },
    name: 'ac-character-transfer-list',
    mixins: [Paginated],
    computed: {
      show () {
        return this.response !== null && this.nonEmpty
      },
      results () {
        if (this.response === null) {
          return []
        } else {
          return this.response.results
        }
      }
    }
  }
</script>

<style scoped>

</style>