<template>
  <ac-base-notification :notification="notification" :asset-link="assetLink">
    <span slot="title"><router-link :to="assetLink">Submission: {{event.data.asset.title}}</router-link></span>
    <span slot="subtitle"><router-link :to="assetLink">By {{event.target.username}}</router-link></span>
  </ac-base-notification>
</template>

<script>
  import AcBaseNotification from './ac-base-notification'
  import Notifiction from '../../mixins/notification'
  export default {
    name: 'ac-new-portfolio-item',
    components: {AcBaseNotification},
    mixins: [Notifiction],
    computed: {
      assetLink () {
        if (this.event.data.asset) {
          return {
            name: 'Submission',
            params: {
              assetID: this.event.data.asset.id
            }
          }
        } else {
          return {}
        }
      }
    }
  }
</script>

<style scoped>

</style>