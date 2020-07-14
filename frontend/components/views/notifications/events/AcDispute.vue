<template>
  <v-list-item>
      <router-link :to="{name: 'Case', params: {orderId: event.target.id, username: viewer.username}}">
        <v-list-item-avatar>
          <img :src="$img(event.data.display, 'notification', true)"/>
        </v-list-item-avatar>
      </router-link>
    <v-list-item-content>
      <v-list-item-title>
        A Dispute has been filed for Order #{{event.target.id}}.
      </v-list-item-title>
    </v-list-item-content>
    <v-list-item-action>
      <v-btn
          @click="claimDispute"
          small
      >Claim
      </v-btn>
    </v-list-item-action>
  </v-list-item>
</template>

<style scoped>
</style>

<script>
import Notification from '../mixins/notification'
import {artCall} from '@/lib/lib'

export default {
  name: 'ac-dispute',
  mixins: [Notification],
  data() {
    return {}
  },
  methods: {
    visitOrder() {
      this.$router.push(
        {name: 'Order', params: {orderId: this.event.target.id, username: this.event.target.buyer.username}},
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
