<template>
  <v-list-tile avatar>
      <router-link :to="{name: 'Case', params: {orderId: event.target.id, username: viewer.username}}">
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)"/>
        </v-list-tile-avatar>
      </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        A Dispute has been filed for Order #{{event.target.id}}.
      </v-list-tile-title>
    </v-list-tile-content>
    <v-list-tile-action>
      <v-btn
          @click="claimDispute"
          small
      >Claim
      </v-btn>
    </v-list-tile-action>
  </v-list-tile>
</template>

<style scoped>
</style>

<script>
import Notification from '../mixins/notification'
import {artCall} from '@/lib'

export default {
  name: 'ac-dispute',
  mixins: [Notification],
  data() {
    return {}
  },
  methods: {
    visitOrder() {
      this.$router.push(
        {name: 'Order', params: {orderId: this.event.target.id, username: this.event.target.buyer.username}}
      )
    },
    claimDispute() {
      artCall({url: `${this.url}claim/`, method: 'post'}).then(this.visitOrder)
    },
  },
  computed: {
    url() {
      return `/api/sales/v1/order/${this.event.target.id}/`
    },
  },
}
</script>
