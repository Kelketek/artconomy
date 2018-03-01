<template>
  <v-list-tile>
    <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification')" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
        <strong>Order #{{event.target.id}} {{message}}</strong>
      </router-link>
      <p v-if="streamingLink">
        <a target="_blank" :href="streamingLink">Your artist is streaming this commission! Click here!</a>
      </p>
    </v-list-tile-content>
  </v-list-tile>
</template>

<style scoped>
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcAction from '../ac-action'
  import Notification from '../../mixins/notification'

  const ORDER_STATUSES = {
    '1': 'has been placed, and is waiting for the artist to accept.',
    '2': 'requires payment to continue.',
    '3': "has been added to the artist's queue!",
    '4': 'is currently in progress!',
    '5': 'is completed and awaiting for your review!',
    '6': 'has been cancelled.',
    '7': 'has been placed under dispute.',
    '8': 'has been completed!',
    '9': 'has been refunded.'
  }

  export default {
    name: 'ac-order-update',
    components: {AcAsset, AcAction},
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      },
      message () {
        return ORDER_STATUSES[this.event.target.status + '']
      },
      streamingLink () {
        if (this.event.target.status === 4) {
          return this.event.target.stream_link
        }
        return ''
      }
    }
  }
</script>