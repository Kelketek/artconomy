<template>
  <router-link :to="{name: 'Submission', params: {'assetID': event.target.id}}">
    <div class="row">
      <div class="col-4 col-lg-2">
        <ac-asset class="p-2" :terse="true" :asset="event.target" thumb-name="notification" />
      </div>
      <div class="col-6">
        <div class="p2">
          <p><strong>Your commission has been favorited!</strong></p>
        </div>
      </div>
    </div>
  </router-link>
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