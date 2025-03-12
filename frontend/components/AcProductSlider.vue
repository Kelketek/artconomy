<template>
  <v-responsive aspect-ratio="16/9">
    <v-lazy v-model="shown">
      <ac-load-section :controller="list" @click="cycle = false">
        <template #default>
          <v-carousel
            v-model="slider"
            :show-arrows="true"
            height="100%"
            :cycle="cycle"
            :hide-delimiters="true"
          >
            <v-carousel-item v-for="product in list.list" :key="product.x!.id">
              <ac-product-preview
                :carousel="true"
                :product="product.x!"
                :eager="eager"
              />
            </v-carousel-item>
          </v-carousel>
        </template>
        <template #loading-spinner>
          <v-carousel
            v-model="slider"
            :show-arrows="false"
            height="100%"
            :hide-delimiters="true"
          >
            <v-carousel-item>
              <v-sheet color="grey-darken-2">
                <v-row class="fill-height" justify="center" align="center">
                  <v-col cols="12" sm="4">
                    <v-row no-gutters align-content="center" justify="center">
                      <v-col cols="6" sm="12" lg="8">
                        <v-responsive
                          aspect-ratio="1"
                          width="100%"
                          height="100%"
                          class="image-skeleton-container"
                        >
                          <v-skeleton-loader
                            type="image"
                            width="100%"
                            max-height="100%"
                            max-width="100%"
                            height="100%"
                          />
                        </v-responsive>
                      </v-col>
                    </v-row>
                  </v-col>
                  <v-col cols="12" md="5" align-self="center">
                    <v-card>
                      <v-card-text class="hidden-sm-and-down">
                        <v-skeleton-loader type="card-avatar" />
                      </v-card-text>
                      <v-card-text class="hidden-md-and-up">
                        <v-skeleton-loader type="list-item-two-line" />
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-sheet>
            </v-carousel-item>
          </v-carousel>
        </template>
      </ac-load-section>
    </v-lazy>
  </v-responsive>
</template>

<script setup lang="ts">
import AcProductPreview from "@/components/AcProductPreview.vue"
import { ListController } from "@/store/lists/controller.ts"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { ref, watch } from "vue"
import type { Product } from "@/types/main"

const props = withDefaults(
  defineProps<{ list: ListController<Product>; eager?: boolean }>(),
  { eager: false },
)

const slider = ref(0)
const cycle = ref(true)
const shown = ref(props.eager)

watch(
  shown,
  (value: boolean) => {
    if (value) {
      props.list.firstRun()
    }
  },
  { immediate: true },
)
</script>

<style>
.image-skeleton-container .v-skeleton-loader__image {
  height: 100%;
}
</style>
