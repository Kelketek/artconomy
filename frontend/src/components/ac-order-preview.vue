<template>
  <div class="col-lg-3 order-preview">
    <div class="card">
      <router-link :to="{name: viewName, params: {username: username, orderID: order.id}}">
        <ac-asset
            :asset="order.product"
            thumb-name="thumbnail"
            :terse="true"
            imgClass="card-img-top"
        ></ac-asset>
      </router-link>
      <div class="card-header">
        <router-link :to="{name: viewName, params: {username: username, orderID: order.id}}">
          {{ order.product.name }}
        </router-link> by
        <router-link v-if="buyer" :to="{name: 'Profile', params: {username: order.seller.username}}">
          {{ order.seller.username }}
        </router-link>
        <router-link v-else :to="{name: 'Profile', params: {username: order.buyer.username}}">
          {{ order.buyer.username }}
        </router-link>
      </div>
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
  </div>
</template>

<script>
  import AcAsset from './ac-asset'
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  export default {
    name: 'ac-order-preview',
    mixins: [Viewer, Perms],
    components: {AcAsset},
    props: ['buyer', 'order', 'username'],
    data () {
      return {
        viewName: this.buyer ? 'Order' : 'Sale'
      }
    }
  }
</script>

<style scoped>

</style>