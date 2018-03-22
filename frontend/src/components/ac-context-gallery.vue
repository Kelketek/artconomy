<template>
  <v-card v-if="assets && assets.length">
    <v-layout v-if="assets.length === 1" row wrap>
      <v-flex xs12  class="pl-2 pr-2 pt-3 pb-3">
        <ac-gallery-preview
            :asset="displayed"
            containerStyle="min-height: 50rem;"
            thumb-name="gallery"
            :contain="true"
        />
      </v-flex>
    </v-layout>
    <v-layout v-else row wrap>
      <v-flex xs12 lg9 class="pl-2 pr-2 pt-3 pb-3">
        <ac-gallery-preview
            :asset="displayed"
            containerStyle="min-height: 50rem;"
            thumb-name="gallery"
            :contain="true"
        />
        <v-flex class="text-xs-center mt-4 hidden-md-and-down">
          <router-link :to="to">
            <v-btn v-if="moreToLoad" color="primary">
              {{seeMoreText}}
            </v-btn>
          </router-link>
        </v-flex>
      </v-flex>
      <v-flex sm12 lg3 class="pl-2 pr-2 pt-3 pb-3">
        <v-layout row wrap>
          <ac-gallery-preview v-for="(asset, key, index) in assets"
                              :key="key" :id="'asset-' + key"
                              v-if="asset.id !== displayed.id"
                              :asset="asset"
                              lg12 md4 sm6 xs12
                              class="pr-1 pl-1"
          />
        </v-layout>
      </v-flex>
      <v-flex xs12 class="text-xs-center mb-2 hidden-lg-and-up">
        <router-link :to="to">
          <v-btn v-if="moreToLoad" color="primary">
            {{seeMoreText}}
          </v-btn>
        </router-link>
      </v-flex>
    </v-layout>
  </v-card>
</template>

<script>
  import AcGalleryPreview from './ac-gallery-preview'

  export default {
    components: {AcGalleryPreview},
    props: ['to', 'showcased', 'totalPieces', 'assets', 'seeMoreText'],
    computed: {
      displayed () {
        if (this.showcased) {
          return this.showcased
        }
        return this.assets[0]
      },
      moreToLoad () {
        return this.totalPieces > 4
      }
    }
  }
</script>