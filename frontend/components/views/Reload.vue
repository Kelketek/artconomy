<template>
  <div></div>
</template>
<script>
export default {
  beforeCreate() {
    const path = this.$route.params.path
    this.$router.replace('/')
    this.$router.replace(path)
  },
}
</script>
