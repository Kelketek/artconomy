<template>
  <div></div>
</template>

<script>
  export default {
    name: 'NotFound',
    data () {
      return {}
    },
    mounted () {
      this.$root.errorCode = 404
    }
  }
</script>

<style scoped>

</style>