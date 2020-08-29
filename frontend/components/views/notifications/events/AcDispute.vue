<template>
  <v-list-item>
      <router-link :to="casePath">
        <v-list-item-avatar>
          <img :src="$img(event.data.display, 'notification', true)"/>
        </v-list-item-avatar>
      </router-link>
    <v-list-item-content>
      <v-list-item-title>
        A Dispute has been filed for Deliverable #{{event.target.id}}.
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
      this.$router.push(this.casePath)
    },
    claimDispute() {
      artCall({url: `${this.url}claim/`, method: 'post'}).then(this.visitOrder)
    },
  },
  computed: {
    url() {
      return `/api/sales/v1/order/${this.event.target.order.id}/deliverables/${this.event.target.id}/`
    },
    casePath() {
      return {
        name: 'CaseDeliverableOverview',
        params: {orderId: this.event.target.order.id, username: this.viewerName, deliverableId: this.event.target.id},
      }
    },
  },
}
</script>
