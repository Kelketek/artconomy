<template>
  <div id="home-page">
    <v-container fluid v-if="viewer !== null && !viewer.username" style="margin-top: -48px">
      <v-layout row wrap class="intro">
        <v-jumbotron class="home-banner darken-3">
          <v-container fluid fill-height>
            <v-layout align-center row wrap>
              <v-flex xs12 md10 offset-md1>
                <h1>Bring your characters to life</h1>
                <h2>by commissioning artists</h2>
                <v-btn color="primary" class="mt-2" :to="{name: 'Login', params: {tabName: 'register'}}">Get Started</v-btn>
                or
                <v-btn color="purple" class="mt-2" @click="$vuetify.goTo('#intro-start', {offset: -60})">Learn More</v-btn>
              </v-flex>
            </v-layout>
          </v-container>
        </v-jumbotron>
      </v-layout>
    </v-container>
  <v-container class="home-main">
    <v-card>
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>Recent Commissions</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <ac-asset-gallery
        endpoint="/api/profiles/v1/recent-commissions/" :limit="4" :no-pagination="true"
        :to="{name: 'RecentArt', params: {tabName: 'all'}}"
        see-more-text="See more art!"
    />
    <v-card>
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>New Products</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        <v-btn color="primary" :to="{name: 'Search', params: {tabName: 'products'}}">Search Products</v-btn>
      </v-flex>
    </v-layout>
    <store class="pt-2" endpoint="/api/sales/v1/new-products/" :limit="20" />
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        <v-btn :to="{name: 'WhoIsOpen', params: {tabName: 'all'}}" color="primary">See more products</v-btn>
      </v-flex>
    </v-layout>
    <v-card>
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>Recent Art</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <ac-asset-gallery
        endpoint="/api/profiles/v1/recent-submissions/" :limit="8" :no-pagination="true"
        :to="{name: 'RecentArt', params: {tabName: 'all'}}"
        see-more-text="See more art!"
    />
    </v-container>
    <v-container v-if="viewer !== null && !viewer.username">
      <v-layout row wrap id="intro-start">
        <v-flex xs12 text-xs-center>
          <img class="home-logo" src="/static/images/logo.svg"/>
        </v-flex>
        <v-flex xs12 text-xs-center class="home-title">
          <h1>Welcome to Artconomy</h1>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12 md6 text-xs-center>
          <img class="demo-img" src="/static/images/characterbrowse.png" />
        </v-flex>
        <v-flex xs12 md6 text-xs-center>
          <h3>Upload and catalog your characters</h3>
          <p>Have a character you want to show off? Now you have the tools to do it, for free!</p>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12 md6 text-xs-center order-sm-2>
          <h3>Commission Artists</h3>
          <p>Have a character in mind but need help bringing it to life? Have an artist make a reference sheet, and many more to stylize your characters as much as you please.</p>
          <p>See artists by rating and pricing, and commission with confidence.</p>
          <h3>Are you an artist?</h3>
          <p>Get a free shop where people can commission you!</p>
          <p>Use built-in communications tools for helping clients keep track of your progress.</p>
          <p>Have the safety and assurance of contracts and escrow payments-- no more worrying about getting paid!</p>
        </v-flex>
        <v-flex xs12 md6 text-xs-center>
          <img class="demo-img-sm" src="/static/images/product.png" />
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12 sm5 text-xs-center text-sm-right>
          <v-btn color="primary" :to="{name: 'FAQ'}">Read our FAQ</v-btn>
        </v-flex>
        <v-flex xs12 sm2 text-xs-center text-sm-center pt-2><strong>OR</strong></v-flex>
        <v-flex xs12 sm5 text-xs-center text-sm-left>
          <v-btn color="purple" :to="{name: 'Login', params: {tabName: 'register'}}">Get Started!</v-btn>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<style>
  .home-logo {
    width: 25%;
    margin-bottom: 2rem;
  }
  .home-title {
    margin-bottom: 2rem;
  }
  img.demo-img {
    max-width: 100%;
  }
  img.demo-img-sm {
    max-width: 50%;
  }
  .home-banner {
    background-size: cover;
    background: url("/static/images/banner.jpg") fixed center;
  }
  .home-banner h1 {
    font-size: 4rem;
    font-weight: lighter;
  }
  .home-banner h2 {
    font-size: 2rem;
    font-weight: normal;
  }
</style>

<script>
  import { setMetaContent } from '../lib'
  import AcAssetGallery from './ac-asset-gallery'
  import Characters from './Characters'
  import Store from './Store'

  export default {
    components: {
      Store,
      Characters,
      AcAssetGallery},
    name: 'Home',
    created () {
      document.title = 'Artconomy-- Where artists and commissioners meet!'
      setMetaContent('description', 'Artconomy lets you find artists to draw your personal characters.')
    }
  }
</script>
