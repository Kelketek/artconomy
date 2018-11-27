<template>
  <v-flex v-bind="$attrs" class="product-preview">
    <v-card>
      <ac-frameable-link :i-frame="iFrame" :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
        <v-img
            :contain="contain"
            :src="$img(product, 'thumbnail')"
            :aspect-ratio="1"
        >
            <ac-asset
                :asset="product"
                thumb-name="thumbnail"
                :terse="true"
                :text-only="true"
            />
        </v-img>
      </ac-frameable-link>
      <v-card-title>
        <div>
          <ac-frameable-link :i-frame="iFrame" :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
            {{ product.name }}
          </ac-frameable-link> by
          <ac-frameable-link :i-frame="iFrame" :to="{name: 'Profile', params: {username: product.user.username, tabName: 'products'}}">
            {{ product.user.username }}
            <ac-frameable-link :i-frame="iFrame" v-if="!product.user.escrow_disabled" :to="{name: 'FAQ', params: {tabName: 'buying-and-selling', subTabName: 'shield'}}">
              <v-tooltip bottom>
                <v-icon slot="activator" class="green--text pl-2">fa-shield</v-icon>
                <span>Protected by Artconomy Shield</span>
              </v-tooltip>
            </ac-frameable-link>
          </ac-frameable-link>
          <ac-frameable-link :i-frame="iFrame" :to="{name: 'Ratings', params: {username: product.user.username}}" v-if="product.user.stars">
            <ac-rating :value="product.user.stars" class="highlight-icon"></ac-rating>
          </ac-frameable-link>
        </div>
      </v-card-title>
      <ac-frameable-link :i-frame="iFrame" :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
        <div class="card-block product-info">
          <div class="extra-details text-xs-center">
            <div class="full-width">
              <strong class="day-count">{{turnaround}}</strong> days <br />
              turnaround
            </div>
          </div>
          <div class="price-container text-xs-center mt-2">
            <span v-if="product.price > 0">Starting at</span>
            <span v-else>Starts</span>
            <div class="price-highlight" v-if="product.price > 0">
              <sup class="mini-dollar">$</sup>{{ product.price }}
            </div>
            <div v-else class="price-highlight">
              FREE
            </div>
          </div>
        </div>
      </ac-frameable-link>
    </v-card>
  </v-flex>
</template>

<script>
  import AcAsset from './ac-asset'
  import AcRating from './ac-rating'
  import AcFrameableLink from './ac-frameable-link'
  export default {
    name: 'ac-product-preview',
    props: ['product', 'contain', 'iFrame'],
    computed: {
      turnaround () {
        return Math.ceil(this.product.expected_turnaround)
      }
    },
    components: {AcFrameableLink, AcRating, AcAsset}
  }
</script>

<style scoped>
  .price-container {
    flex-grow: 1;
  }
  .product-info {
    width: 100%;
    display: flex;
    flex-direction: row;
  }
  .mini-dollar {
    font-size: 1.2rem;
    position: relative;
    top: -1rem;
  }
  .full-width {
    width: 100%;
  }
  .day-count {
    font-size: 2rem;
  }
  .extra-details {
    display: flex;
    position: relative;
    height: 100%;
    flex-grow: 1;
    top: .5rem;
  }
  .price-highlight {
    font-weight: bold;
    font-size: 2.5rem;
  }
</style>