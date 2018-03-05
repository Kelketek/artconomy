<template>
  <v-app dark>
    <nav-bar />
    <v-content style="padding-top: 0">
      <v-container fluid>
        <div v-if="$root.errorCode !== null" class="container error-container">
          <div class="row">
            <div class="col-12 text-xs-center">
              <img class="error-logo" src="/static/images/logo.svg"/>
            </div>
            <div class="col-12 text-xs-center home-title">
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
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
  import NavBar from './components/NavBar'
  import AcFooter from './components/ac-footer'
  export default {
    name: 'app',
    data () {
      return {}
    },
    components: {
      AcFooter,
      NavBar},
    props: ['user']
  }
</script>

<style lang="scss">
  a {
    text-decoration: none;
  }
  .error-logo {
    width: 25%;
    margin-bottom: 2rem;
  }
  .pb-10 {
    padding-bottom: 6rem !important;
  }
  .error-title {
    margin-bottom: 2rem;
  }
</style>
