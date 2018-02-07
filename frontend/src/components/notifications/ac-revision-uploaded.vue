<template>
    <div class="row">
      <div class="col-4 col-lg-2">
        <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
          <ac-asset class="p-2" :terse="true" :asset="event.data.revision" thumb-name="notification" />
        </router-link>
      </div>
      <div class="col-6">
        <router-link :to="{name: 'Order', params: {orderID: event.target.id, username: viewer.username}}">
          <div class="pt-1 pb-1">
            <p><strong>A revision has been uploaded for Order #{{event.target.id}}</strong></p>
          </div>
        </router-link>
      </div>
    </div>
</template>

<style scoped>
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcAction from '../ac-action'

  export default {
    name: 'ac-revision-uploaded',
    components: {AcAsset, AcAction},
    props: ['event'],
    data () {
      return {}
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      }
    }
  }
</script>