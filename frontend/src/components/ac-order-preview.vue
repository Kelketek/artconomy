<template>
  <v-flex xs12 md4 lg3 class="order-preview">
    <v-card>
      <router-link :to="{name: viewName, params: {username: username, orderID: order.id}}">
        <v-card-media
            :contain="contain"
            :src="$img(order.product, 'thumbnail')"
        >
          <ac-asset
              :asset="order.product"
              thumb-name="thumbnail"
              :terse="true"
              :text-only="true"
          />
        </v-card-media>
      </router-link>
      <v-card-title>
        <div>
          <router-link :to="{name: viewName, params: {username: username, orderID: order.id}}">
            {{ order.product.name }}
          </router-link> <span v-if="!buyer">commissioned </span>by
          <router-link v-if="buyer" :to="{name: 'Profile', params: {username: order.seller.username}}">
            {{ order.seller.username }}
          </router-link>
          <router-link v-else :to="{name: 'Profile', params: {username: order.buyer.username}}">
            {{ order.buyer.username }}
          </router-link>
        </div>
      </v-card-title>
      <v-card-title>
        <div>
          <router-link :to="{name: viewName, params: {username: username, orderID: order.id}}">
            <div class="card-block order-info pl-2">
              Characters:
              <ul>
                <li v-for="char in order.characters" :key="char.id">
                  {{ char.name }}<span v-if="char.user.username !== order.buyer.username"> ({{char.user.username}})</span>
                </li>
              </ul>
            </div>
          </router-link>
        </div>
      </v-card-title>
    </v-card>
  </v-flex>
</template>

<script>
  import AcAsset from './ac-asset'
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  export default {
    name: 'ac-order-preview',
    mixins: [Viewer, Perms],
    components: {AcAsset},
    props: ['buyer', 'order', 'username', 'contain'],
    data () {
      return {
        viewName: this.buyer ? 'Order' : 'Sale'
      }
    }
  }
</script>
