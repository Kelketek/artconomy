<template>
  <v-responsive v-if="$vuetify.breakpoint.smAndDown || mini" aspect-ratio="1" :class="{unavailable}">
    <v-card>
      <v-layout column class="pt-2">
        <v-layout row wrap>
          <v-flex xs8 offset-xs2>
            <ac-link :to="productLink">
              <ac-asset :text="false" :asset="product.primary_submission" thumb-name="thumbnail"></ac-asset>
            </ac-link>
          </v-flex>
        </v-layout>
        <v-flex>
          <v-card-text class="pb-2">
            <v-layout row wrap>
              <v-flex xs12><ac-link :to="productLink">{{product.name}}</ac-link></v-flex>
              <v-flex xs12>
                <v-layout row>
                  <v-flex grow><small>From</small> ${{product.price.toFixed(2)}}</v-flex>
                  <v-flex shrink>
                    <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                      <v-tooltip bottom v-if="!product.escrow_disabled">
                        <v-icon slot="activator" color="green" class="pl-1" small>fa-shield</v-icon>
                        <span>Protected by Artconomy Shield</span>
                      </v-tooltip>
                    </ac-link>
                  </v-flex>
                </v-layout>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-flex>
      </v-layout>
    </v-card>
  </v-responsive>
  <v-card class="product-preview" :class="{unavailable}" v-else>
    <ac-link :to="productLink">
      <ac-asset :asset="product.primary_submission" thumb-name="thumbnail"></ac-asset>
    </ac-link>
    <v-card-text class="pt-2">
      <v-layout row>
        <v-flex text-xs-left>
          <ac-link :to="productLink">{{product.name}}</ac-link>
          By
          <ac-link :to="{name: 'Products', params: {username: product.user.username}}">{{product.user.username}}</ac-link>
        </v-flex>
        <v-spacer></v-spacer>
      </v-layout>
      <v-layout row>
        <v-flex shrink d-flex>
          <v-layout column align-content-end align-end>
            <v-spacer></v-spacer>
            <ac-link :to="productLink">
              <v-flex shrink>
                <ac-link :to="productLink">
                  <span class="days-turnaround">{{turnaround}}</span> days
                </ac-link>
              </v-flex>
              <v-flex>turnaround</v-flex>
            </ac-link>
          </v-layout>
        </v-flex>
        <v-spacer></v-spacer>
        <v-flex shrink d-flex>
          <v-layout column>
            <v-flex>
              <v-layout row>
                <ac-link :to="{name: 'Ratings', params: {username: product.user.username}}" v-if="product.user.stars">
                  <v-rating dense small half-increments :value="product.user.stars" color="primary"></v-rating>
                </ac-link>
                <v-spacer v-else></v-spacer>
                <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                  <v-tooltip bottom v-if="!product.escrow_disabled">
                    <v-icon slot="activator" color="green" class="pl-1">fa-shield</v-icon>
                    <span>Protected by Artconomy Shield</span>
                  </v-tooltip>
                </ac-link>
              </v-layout>
            </v-flex>
            <ac-link :to="productLink">
              <v-flex shrink>
                Starting at
              </v-flex>
              <v-flex>
                <span class="currency-notation" v-if="product.price">$</span>
                <span class="price-display">{{product.price.toFixed(2)}}</span>
              </v-flex>
            </ac-link>
          </v-layout>
        </v-flex>
      </v-layout>
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
    text-decoration: none;
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
