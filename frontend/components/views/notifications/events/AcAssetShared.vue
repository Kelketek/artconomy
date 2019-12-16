<template>
  <v-list-item>
    <router-link :to="assetLink">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-item-avatar>
          <img :src="$img(event.data.display, 'notification', true)" alt="">
        </v-list-item-avatar>
      </v-badge>
    </router-link>
    <v-list-item-content>
      <v-list-item-title>
        <router-link :to="assetLink">
          A submission was shared with you
        </router-link>
      </v-list-item-title>
      <v-list-item-subtitle>
        <router-link :to="assetLink">"{{event.data.asset.title}}" was shared by {{event.data.user.username}}
        </router-link>
      </v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
import Notification from '../mixins/notification'

export default {
  name: 'ac-asset-shared',
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    assetLink() {
      if (this.event.data.asset) {
        return {name: 'Submission', params: {assetID: this.event.data.asset.id}}
      } else {
        return {}
      }
    },
  },
}
</script>

<style scoped>

</style>
