<template>
  <v-list-tile avatar>
    <v-list-tile-content>
      <router-link :to="{name: 'Case', params: {orderID: event.target.id, username: viewer.username}}">
        <v-list-tile-avatar>
          <img :src="$img(event.target.product, 'notification', true)" />
        </v-list-tile-avatar>
      </router-link>
      <v-list-tile-title>
        A Dispute has been filed for Order #{{event.target.id}}.
      </v-list-tile-title>
    </v-list-tile-content>
    <v-list-tile-action>
      <ac-action
          method="POST"
          :url="`${this.url}claim/`"
          :success="visitOrder"
          small
      >Claim</ac-action>
    </v-list-tile-action>
  </v-list-tile>
</template>

<style scoped>
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcAction from '../ac-action'
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-dispute',
    components: {AcAsset, AcAction},
    mixins: [Notification],
    data () {
      return {}
    },
    methods: {
      visitOrder () {
        this.$router.push(
          {name: 'Order', params: {orderID: this.event.target.id, username: this.event.target.buyer.username}}
        )
      }
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      }
    }
  }
</script>