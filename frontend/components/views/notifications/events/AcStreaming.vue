<template>
  <ac-base-notification :notification="notification" :href-link="streamLink">
    <template v-slot:title><a :href="streamLink"
                              target="_blank">{{ event.data.order.seller.username }} is streaming!</a></template>
  </ac-base-notification>
</template>

<script>
import AcBaseNotification from './AcBaseNotification'
import Notifiction from '../mixins/notification'

export default {
  name: 'ac-streaming',
  components: {AcBaseNotification},
  mixins: [Notifiction],
  computed: {
    streamLink() {
      return this.event.data.order.stream_link || '#'
    },
  },
}
</script>

<style scoped>

</style>
