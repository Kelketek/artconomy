<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">You've been credited for a referral!</router-link>
    </template>
    <template v-slot:subtitle>
      <router-link
          :to="assetLink">You've received a month of Artconomy Landscape.
      </router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notifiction from '../mixins/notification.ts'

export default {
  name: 'ac-landscape-referral',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'LinksAndStats',
        params: {
          username: this.event.target.username,
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
