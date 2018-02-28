<template>
  <v-flex xs12 md4 lg3 class="product-preview">
    <v-card>
      <router-link :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
        <v-card-media
            :contain="contain"
            :src="$img(product, 'thumbnail')"
        >
            <ac-asset
                :asset="product"
                thumb-name="thumbnail"
                :terse="true"
                :text-only="true"
            />
        </v-card-media>
      </router-link>
      <v-card-title>
        <div>
          <router-link :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
            {{ product.name }}
          </router-link> by
          <router-link :to="{name: 'Profile', params: {username: product.user.username}}">
            {{ product.user.username }}
          </router-link>
        </div>
      </v-card-title>
      <router-link :to="{name: 'Product', params: {username: product.user.username, productID: product.id}}">
        <div class="card-block product-info">
          <div class="extra-details text-xs-center">
            <div class="full-width">
              <strong class="day-count">{{product.expected_turnaround}}</strong> days <br />
              turnaround
            </div>
          </div>
          <div class="price-container text-xs-center mt-2">
            Starting at
            <div class="price-highlight">
              <sup class="mini-dollar">$</sup>{{ product.price }}
            </div>
          </div>
        </div>
      </router-link>
    </v-card>
  </v-flex>
</template>

<script>
  import AcAsset from './ac-asset'
  export default {
    name: 'ac-product-preview',
    props: ['product', 'contain'],
    components: {AcAsset}
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