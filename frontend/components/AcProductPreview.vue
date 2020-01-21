<template>
  <v-responsive v-if="$vuetify.breakpoint.smAndDown || mini" aspect-ratio="1" :class="{unavailable}" class="product-preview">
    <v-card>
      <v-container fluid class="pa-2">
        <v-row no-gutters class="pb-2" >
          <v-col cols="8" offset="2">
            <ac-link :to="productLink">
              <ac-asset :text="false" :asset="product.primary_submission" thumb-name="thumbnail" />
            </ac-link>
          </v-col>
        </v-row>
        <v-row no-gutters>
          <v-col cols="12"><ac-link :to="productLink">{{product.name}}</ac-link></v-col>
          <v-col cols="12">
            <v-row no-gutters>
              <v-col class="grow" ><small>From</small> ${{product.starting_price.toFixed(2)}}</v-col>
              <v-col class="no-underline shrink">
                <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                  <v-tooltip bottom v-if="!product.escrow_disabled">
                    <template v-slot:activator="{on}">
                      <v-icon color="green" class="pl-1" small v-on="on">fa-shield</v-icon>
                    </template>
                    <span>Protected by Artconomy Shield</span>
                  </v-tooltip>
                </ac-link>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-responsive>
  <v-card class="product-preview" :class="{unavailable}" v-else>
    <ac-link :to="productLink">
      <ac-asset :asset="product.primary_submission" thumb-name="thumbnail" />
    </ac-link>
    <v-card-text class="pt-2">
      <v-row no-gutters >
        <v-col class="text-left" >
          <ac-link :to="productLink">{{product.name}}</ac-link>
          By
          <ac-link :to="{name: 'Products', params: {username: product.user.username}}">{{product.user.username}}</ac-link>
        </v-col>
        <v-spacer />
      </v-row>
      <v-row no-gutters>
        <v-col>
          <v-row no-gutters>
            <ac-link :to="{name: 'Ratings', params: {username: product.user.username}}" v-if="product.user.stars">
              <v-rating dense small half-increments :value="product.user.stars" color="primary" />
            </ac-link>
            <v-spacer v-else />
            <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
              <v-tooltip bottom v-if="!product.escrow_disabled">
                <template v-slot:activator="{on}">
                  <v-icon slot="activator" color="green" class="pl-1">fa-shield</v-icon>
                </template>
                <span>Protected by Artconomy Shield</span>
              </v-tooltip>
            </ac-link>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters class="mt-2">
        <v-col class="shrink d-flex">
          <v-row no-gutters align-content="end" align="end">
            <v-col>
            <v-spacer />
            <ac-link :to="productLink">
              <v-row no-gutters>
                <v-col class="shrink" >
                  <ac-link :to="productLink">
                    <span class="days-turnaround">{{turnaround}}</span> days turnaround
                  </ac-link>
                </v-col>
              </v-row>
            </ac-link>
            </v-col>
          </v-row>
        </v-col>
        <v-spacer />
        <v-col class="shrink d-flex">
          <ac-link :to="productLink">
            <v-row no-gutters>
              <v-col cols="12" class="pb-1">
                Starting at
              </v-col>
              <v-col cols="12">
                <span class="currency-notation" v-if="product.starting_price">$</span>
                <span class="price-display">{{product.starting_price.toFixed(2)}}</span>
              </v-col>
            </v-row>
          </ac-link>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped>
  .days-turnaround, .price-display {
    font-size: 2.5rem;
  }
  .unavailable {
    opacity: .5;
  }
</style>

<style>
  .product-preview a {
    text-decoration: none !important;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import Product from '@/types/Product'
import {Prop} from 'vue-property-decorator'
import AcAsset from '@/components/AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
  @Component({
    components: {AcLink, AcAsset},
  })
export default class AcProductPreview extends Vue {
    @Prop({required: true})
    public product!: Product
    @Prop({default: false})
    public mini!: boolean
    public get productLink() {
      return {name: 'Product', params: {username: this.product.user.username, productId: this.product.id}}
    }
    public get unavailable() {
      return !this.product.available
    }
    public get turnaround() {
      return Math.ceil(this.product.expected_turnaround)
    }
}
</script>
