<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">{{event.target.username}} is open!</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link :to="assetLink">Click here to commission them.</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notifiction from '../mixins/notification.ts'

export default {
  name: 'ac-commissions-open',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Profile',
        params: {
          username: this.event.target.username,
          tabName: 'products',
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
