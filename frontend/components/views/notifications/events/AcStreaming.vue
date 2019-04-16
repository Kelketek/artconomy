<template>
  <ac-base-notification :notification="notification" :href-link="streamLink">
    <span slot="title"><a :href="streamLink"
                          target="_blank">{{ event.data.order.seller.username }} is streaming!</a></span>
    <span slot="avatar"><img :src="event.data.order.seller.avatar_url"/></span>
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
