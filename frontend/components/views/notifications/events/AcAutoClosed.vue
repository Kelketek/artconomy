<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">Your sales have been automatically closed for inactivity.</router-link></span>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'
import {deriveDisplayName} from '@/lib/lib'

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
