<template>
  <v-sheet height="100%" v-if="carousel" :color="$vuetify.theme.themes.dark.darkBase.darken2" class="product-preview">
    <v-row
      class="fill-height"
      justify="center"
      align="center"
    >
      <v-col cols="12" sm="4">
        <v-row no-gutters align-content="center" justify="center">
          <v-col cols="6" sm="12" lg="8">
            <ac-link :to="{name: 'Product', params: {productId: product.id, username: product.user.username}}">
              <ac-asset :asset="product.primary_submission" thumb-name="thumbnail" />
            </ac-link>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" md="5" align-self="center">
        <v-card>
          <v-card-text>
            <v-row class="fill-height" no-gutters>
              <v-col cols="12" class="text-center hidden-sm-and-down title py-3">
                  <ac-link :to="productLink" class="text-center">
                    <div v-html="mdRenderInline(product.name)" class="text-center" />
                  </ac-link>
              </v-col>
              <v-col cols="12" class="text-center hidden-md-and-up">
                <strong><ac-rendered inline="true" tag="span" :value="product.name" /></strong>
              </v-col>
              <v-col cols="12" class="hidden-md-and-up">
                <v-row no-gutters>
                  <v-col class="shrink" align-self="start">
                    From ${{product.starting_price.toFixed(2)}}
                  </v-col>
                  <v-spacer></v-spacer>
                  <v-col class="shrink" align-self="end">
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
              <v-col class="text-center hidden-sm-and-down" cols="12" v-if="!product.escrow_disabled">
                <ac-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
                  <v-icon color="green" class="pr-1">fa-shield</v-icon>
                  <span>Protected by Artconomy Shield</span>
                </ac-link>
              </v-col>
              <v-col cols="6" class="hidden-sm-and-down">
                <v-row class="fill-height" align="center" justify="center" no-gutters>
                  <v-col cols="12" class="text-center no-underline">
                    <ac-link :to="productLink"><span class="days-turnaround">{{turnaround}}</span></ac-link></v-col>
                  <v-col cols="12" class="text-center"><ac-link :to="productLink">days turnaround</ac-link></v-col>
                </v-row>
              </v-col>
              <v-col cols="6" class="hidden-sm-and-down">
                <v-col cols="12" class="pb-1 no-underline">
                  <ac-link :to="productLink">Starting at</ac-link>
                </v-col>
                <v-col cols="12" class="no-underline">
                  <ac-link :to="productLink">
                    <span class="currency-notation" v-if="product.starting_price">$</span>
                    <span class="price-display">{{product.starting_price.toFixed(2)}}</span>
                  </ac-link>
                </v-col>
              </v-col>
              <v-col cols="12" class="hidden-sm-and-down">
                <v-toolbar color="black">
                  <ac-avatar :user="product.user" :show-name="false"></ac-avatar>
                  <v-toolbar-title>{{product.user.username}}</v-toolbar-title>
                </v-toolbar>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-sheet>
  <v-responsive v-else-if="$vuetify.breakpoint.smAndDown || mini" aspect-ratio="1" :class="{unavailable}" class="product-preview">
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
import Component, {mixins} from 'vue-class-component'
import Product from '@/types/Product'
import {Prop} from 'vue-property-decorator'
import AcAsset from '@/components/AcAsset.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcAvatar from '@/components/AcAvatar.vue'
import Formatting from '@/mixins/formatting'
  @Component({
    components: {AcAvatar, AcRendered, AcLink, AcAsset},
  })
export default class AcProductPreview extends mixins(Formatting) {
    @Prop({required: true})
    public product!: Product
    @Prop({default: false})
    public mini!: boolean
    @Prop({default: false})
    public carousel!: boolean
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
