<template>
  <div id="app">
    <ac-navbar :user="user"></ac-navbar>
    <div class="mt-3"></div>
    <router-view v-if="$root.user !== null"/>
    <div v-else class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
  </div>
</template>

<script>
  export default {
    name: 'app',
    props: ['user']
  }
</script>

<style lang="scss">
  @import "./custom-bootstrap.scss";
  @import "../../node_modules/bootstrap/scss/bootstrap.scss";
</style>
