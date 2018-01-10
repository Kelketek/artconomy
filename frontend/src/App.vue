<template>
  <div id="app">
    <nav-bar />
    <div v-if="$root.errorCode !== null" class="container error-container">
      <div class="row">
        <div class="col-sm-12 text-center">
          <img class="error-logo" src="/static/images/logo.svg"/>
        </div>
        <div class="col-sm-12 text-center home-title">
          <h1>Whoops!</h1>
          <p v-if="$root.errorCode === 500">
            Something went wrong. We've notified our developers and will get it fixed as soon as we can!
          </p>
          <p v-else-if="$root.errorCode === 400">
            Something seems wrong with your request. Could you check the URL?
          </p>
          <p v-else-if="$root.errorCode === 404">
            We couldn't find that page. It might not exist or you might not have the right privileges to see it.
          </p>
          <p v-else-if="$root.errorCode === 403">
            Access to this page is restricted. Please make sure you're logged into an account that has access to it.
          </p>
          <p v-else>
            Something weird happened. Could you please contact support and tell us about it?
          </p>
        </div>
      </div>
    </div>
    <router-view v-else-if="$root.user !== null" />
    <div v-else class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
  </div>
</template>

<script>
  import NavBar from './components/NavBar'
  export default {
    name: 'app',
    components: {NavBar},
    props: ['user']
  }
</script>

<style lang="scss">
  @import "./custom-bootstrap.scss";
  @import "../../node_modules/bootstrap/scss/bootstrap.scss";
  .error-logo {
    width: 25%;
    margin-bottom: 2rem;
  }
  .error-title {
    margin-bottom: 2rem;
  }
</style>
