<template>
  <v-list-tile avatar>
    <router-link :to="assetLink">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="$img(event.data.display, 'notification', true)" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="assetLink">
          A submission was shared with you
        </router-link>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        <router-link :to="assetLink">"{{event.data.asset.title}}" was shared by {{event.data.user.username}}</router-link>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-asset-shared',
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      assetLink () {
        if (this.event.data.asset) {
          return {name: 'Submission', params: {assetID: this.event.data.asset.id}}
        } else {
          return {}
        }
      }
    }
  }
</script>

<style scoped>

</style>