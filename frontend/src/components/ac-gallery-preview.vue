<template>
    <v-flex v-bind="$attrs">
      <v-card>
        <router-link :to="{name: 'Submission', params: {assetID: asset.id}}">
          <v-card-media
              :src="$img(asset, thumbName)"
              :contain="contain"
          >
            <ac-asset :asset="asset" :text-only="true" :thumb-name="thumbName" :container-style="containerStyle" />
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
    props: {
      asset: {},
      containerStyle: {},
      thumbName: {
        default: 'thumbnail'
      },
      contain: {
        default: false
      }
    }
  }
</script>
