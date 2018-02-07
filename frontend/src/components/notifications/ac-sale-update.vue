<template>
    <div class="row">
      <div class="col-4 col-lg-2">
        <router-link :to="{name: 'Sale', params: {orderID: event.target.id, username: viewer.username}}">
          <ac-asset class="p-2" :terse="true" :asset="event.data.display" thumb-name="notification" />
        </router-link>
      </div>
      <div class="col-6">
        <router-link :to="{name: 'Sale', params: {orderID: event.target.id, username: viewer.username}}">
          <div class="pt-1 pb-1">
            <p><strong>Sale #{{event.target.id}} {{message}}</strong></p>
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
  const ORDER_STATUSES = {
    '1': 'has been placed, and is awaiting your acceptance!',
    '2': 'is waiting on the commissioner to pay.',
    '3': 'has been added to your queue.',
    '4': 'is currently in progress. Update when you have a revision or the final completed.',
    '5': "is completed and awaiting the commissioner's review.",
    '6': 'has been cancelled.',
    '7': 'has been placed under dispute.',
    '8': 'has been completed!',
    '9': 'has been refunded.'
  }

  export default {
    name: 'ac-sale-update',
    components: {AcAsset, AcAction},
    props: ['event'],
    data () {
      return {}
    },
    computed: {
      url () {
        return `/api/sales/v1/order/${this.event.target.id}/`
      },
      message () {
        return ORDER_STATUSES[this.event.target.status + '']
      },
      streamingLink () {
        if (this.event.target.status === 4) {
          return this.event.target.stream_link
        }
        return ''
      }
    }
  }
</script>