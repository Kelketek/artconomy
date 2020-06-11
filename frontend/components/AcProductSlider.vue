<template>
  <v-responsive aspect-ratio="16/9">
    <ac-load-section :controller="list">
      <v-carousel :show-arrows="true" height="100%" v-model="slider" :cycle="cycle" :hide-delimiters="true" @click="cycle=false">
        <v-carousel-item v-for="product in list.list" :key="product.x.id">
          <ac-product-preview :carousel="true" :product="product.x" />
        </v-carousel-item>
      </v-carousel>
    </ac-load-section>
  </v-responsive>
</template>

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
