<template>
    <v-flex xs12 md4 lg3>
      <v-card>
        <router-link :to="{name: 'Submission', params: {assetID: asset.id}}">
          <v-card-media
              :src="$img(asset, 'thumbnail')"
          >
            <ac-asset :asset="asset" :text-only="true" thumb-name="thumbnail" />
          </v-card-media>
        </router-link>
        <v-card-title>
          <router-link :to="{name: 'Submission', params: {assetID: asset.id}}">
            <div class="text-xs-center">{{ asset.title }}</div>
            <div><v-icon>favorite</v-icon> {{ asset.favorite_count }} <v-icon>comment</v-icon> {{ asset.comment_count }}</div>
          </router-link>
        </v-card-title>
      </v-card>
    </v-flex>
</template>

<script>
  import AcAsset from './ac-asset'

  export default {
    components: {AcAsset},
    name: 'ac-gallery-preview',
    props: ['asset']
  }
</script>

<style>
  .character-gallery-image img {
    max-width: 100%;
    width: 100%;
    min-height: 100%;
    object-fit: cover;
    position: relative;
    z-index: 2;
  }
</style>