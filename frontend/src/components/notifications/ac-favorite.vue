<template>
  <v-list-tile avatar>
    <router-link :to="{name: 'Submission', params: {'assetID': event.target.id}}">
      <v-list-tile-avatar>
        <img :src="$img(event.target, 'notification', true)" />
      </v-list-tile-avatar>
    </router-link>
    <v-list-tile-title>
        Your piece has been favorited!
    </v-list-tile-title>
  </v-list-tile>
</template>

<script>
  import AcAsset from '../ac-asset'
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-favorite',
    components: {AcAsset},
    mixins: [Notification],
    data () {
      return {}
    }
  }
</script>