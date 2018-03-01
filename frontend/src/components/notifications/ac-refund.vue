<template>
  <div class="col-4">
    <ac-asset :terse="true" :asset="event.target"></ac-asset>
  </div>
</template>

<script>
  import AcAsset from '../ac-asset'
  import Notification from '../../mixins/notification'
  export default {
    name: 'ac-refund',
    mixins: [Notification],
    components: {AcAsset},
    data () {
      return {}
    }
  }
</script>