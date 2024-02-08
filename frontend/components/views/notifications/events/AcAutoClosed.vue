<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <template v-slot:title>
      <router-link :to="assetLink">Your sales have been automatically closed for inactivity.</router-link>
    </template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification.vue'
import Notifiction from '../mixins/notification.ts'

export default {
  name: 'ac-auto-closed',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    assetLink() {
      return {
        name: 'Sales',
        params: {
          username: this.viewer.username,
        },
      }
    },
  },
}
</script>

<style scoped>

</style>
