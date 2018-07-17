<template>
  <v-list-tile avatar>
    <router-link :to="pmLink">
      <v-badge left overlap>
        <span slot="badge" v-if="!notification.read">*</span>
        <v-list-tile-avatar>
          <img :src="event.target.sender.avatar_url" >
        </v-list-tile-avatar>
      </v-badge>
    </router-link>
    <v-list-tile-content>
      <v-list-tile-title>
        <router-link :to="pmLink">
          New Private message from {{event.target.sender.username}}
        </router-link>
      </v-list-tile-title>
      <v-list-tile-sub-title>
        <router-link :to="pmLink">Subject: {{event.target.subject}}</router-link>
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
</template>

<script>
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-new-pm',
    mixins: [Notification],
    data () {
      return {}
    },
    computed: {
      pmLink () {
        return {name: 'Message', params: {messageID: this.event.target.id}}
      }
    }
  }
</script>

<style scoped>

</style>