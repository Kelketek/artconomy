<template>
    <div class="row">
      <div class="col-4 col-lg-2">
        <router-link :to="{name: 'Case', params: {orderID: event.target.id, username: viewer.username}}">
          <ac-asset class="p-2" :terse="true" :asset="event.target.product" thumb-name="notification" />
        </router-link>
      </div>
      <div class="col-6">
        <div class="pt-1 pb-1">
          <p><strong>A Dispute has been filed for Order #{{event.target.id}}.</strong></p>
          <ac-action
              method="POST"
              :url="`${this.url}claim/`"
              :success="visitOrder"
          >Claim</ac-action>
        </div>
      </div>
    </div>
</template>

<style scoped>
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcAction from '../ac-action'
  export default {
    name: 'ac-dispute',
    components: {AcAsset, AcAction},
    props: ['event'],
    data () {
      return {}
    },
    methods: {
      visitOrder () {
        this.$router.push(
          {name: 'Order', params: {orderID: this.event.target.id, username: this.event.target.buyer.username}}
        )
      }
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      }
    }
  }
</script>