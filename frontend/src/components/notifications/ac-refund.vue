<template>
  <div class="col-sm-4">
    <ac-asset :terse="true" :asset="event.target"></ac-asset>
  </div>
</template>

<script>
  import AcAsset from '../ac-asset'
  export default {
    name: 'ac-refund',
    props: ['event'],
    components: {AcAsset},
    data () {
      return {}
    }
  }
</script>