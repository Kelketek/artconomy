<template>
  <v-responsive aspect-ratio="16/9">
    <ac-load-section :controller="list" @click.native="cycle=false">
      <template v-slot:default>
        <v-carousel :show-arrows="true" height="100%" v-model="slider" :cycle="cycle" :hide-delimiters="true">
          <v-carousel-item v-for="product in list.list" :key="product.x.id">
            <ac-product-preview :carousel="true" :product="product.x" />
          </v-carousel-item>
        </v-carousel>
      </template>
      <template v-slot:loading-spinner>
        <v-carousel :show-arrows="false" height="100%" v-model="slider" :hide-delimiters="true">
          <v-carousel-item>
            <v-sheet height="100%" :color="$vuetify.theme.themes.dark.darkBase.darken2">
              <v-row
                class="fill-height"
                justify="center"
                align="center"
              >
                <v-col cols="12" sm="4">
                  <v-row no-gutters align-content="center" justify="center">
                    <v-col cols="6" sm="12" lg="8">
                      <v-responsive aspect-ratio="1" width="100%" height="100%" class="image-skeleton-container">
                        <v-skeleton-loader
                          type="image"
                          width="100%"
                          max-height="100%"
                          max-width="100%"
                          height="100%" />
                      </v-responsive>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="12" md="5" align-self="center">
                  <v-card>
                    <v-card-text class="hidden-sm-and-down">
                      <v-skeleton-loader type="card-avatar"></v-skeleton-loader>
                    </v-card-text>
                    <v-card-text class="hidden-md-and-up">
                      <v-skeleton-loader type="list-item-two-line"></v-skeleton-loader>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-sheet>
          </v-carousel-item>
        </v-carousel>
      </template>
    </ac-load-section>
  </v-responsive>
</template>

<style>
  .image-skeleton-container .v-skeleton-loader__image {
    height: 100%;
  }
</style>

<script lang="ts">
import Component from 'vue-class-component'
import Vue from 'vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {Prop} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
@Component({
  components: {AcLoadSection, AcProductPreview},
})
export default class AcProductSlider extends Vue {
  @Prop()
  public list!: ListController<Product>

  public slider = 0
  public cycle = true
}
</script>
