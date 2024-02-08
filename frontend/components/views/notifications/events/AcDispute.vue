<template>
  <v-list-item>
    <router-link :to="casePath">
      <template v-slot:prepend>
        <img :src="$img(event.data.display, 'notification', true)"/>
      </template>
    </router-link>
    <v-list-item-title>
      A Dispute has been filed for Deliverable #{{event.target.id}}.
    </v-list-item-title>
    <template v-slot:append>
      <v-btn
          @click="claimDispute"
          variant="flat"
          small
      >Claim
      </v-btn>
    </template>
  </v-list-item>
</template>

<style scoped>
</style>

<script>
import Notification from '../mixins/notification.ts'
import {artCall} from '@/lib/lib.ts'

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
      artCall({
        url: `${this.url}claim/`,
        method: 'post',
      }).then(this.visitOrder)
    },
  },
  computed: {
    url() {
      return `/api/sales/order/${this.event.target.order.id}/deliverables/${this.event.target.id}/`
    },
    casePath() {
      return {
        name: 'CaseDeliverableOverview',
        params: {
          orderId: this.event.target.order.id,
          username: this.viewerName,
          deliverableId: this.event.target.id,
        },
      }
    },
  },
}
</script>
