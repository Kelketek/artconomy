<template>
  <div></div>
</template>
<script>
  export default {
    beforeCreate () {
      const path = this.$route.params.path
      this.$router.history.replace('/')
      this.$router.history.replace(path)
    }
  }
</script>