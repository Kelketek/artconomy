<template>
  <div id="home-page">
    <v-container fluid v-if="viewer !== null && !viewer.username" style="margin-top: -48px">
      <v-layout row wrap class="intro">
        <v-responsive class="home-banner darken-3" max-width="100%">
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
        </v-responsive>
      </v-layout>
    </v-container>
  <v-container class="home-main">
    <v-alert
        :value="showMailingPrompt"
        type="info"
        class="mb-2"
    >
      <div v-if="answered">Ok!</div>
      <div v-else>
        <p><strong>Would you like to keep up to date on the latest Artconomy news by joining our mailing list?</strong></p>
        <v-btn color="red" @click="mailAnswer('DELETE')">No, thank you.</v-btn> <v-btn color="purple" @click="mailAnswer('POST')">Yes, please!</v-btn>
      </div>
    </v-alert>
    <v-layout row wrap>
      <v-flex xs12><v-img :src="`/static/images/${randomBanner.file}`"></v-img></v-flex>
      <v-flex xs12><p>Banner by <router-link :to="{name: 'Profile', params: {username: randomBanner.username}}">{{randomBanner.username}}</router-link></p></v-flex>
    </v-layout>
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
    <ac-product-list class="pt-2" endpoint="/api/sales/v1/new-products/" :limit="20" :no-pagination="true" />
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
  import {artCall, setMetaContent} from '../lib'
  import AcAssetGallery from './ac-asset-gallery'
  import Characters from './Characters'
  import Viewer from '../mixins/viewer'
  import AcProductList from './ac-product-list'

  export default {
    components: {
      AcProductList,
      Characters,
      AcAssetGallery},
    mixins: [Viewer],
    data () {
      return {
        answered: false,
        banners: [
          {file: 'halcy0n-artconomy-banner-A1-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-A2-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-A3-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-A4-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-B1-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-B2-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-B3-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-B4-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-C1-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-C2-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-C3-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-C4-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-D1-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-D2-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-D3-1440x200.png', username: 'Halcyon'},
          {file: 'halcy0n-artconomy-banner-D4-1440x200.png', username: 'Halcyon'}
        ]
      }
    },
    name: 'Home',
    created () {
      document.title = 'Artconomy-- Where artists and commissioners meet!'
      setMetaContent('description', 'Artconomy lets you find artists to draw your personal characters.')
    },
    methods: {
      refreshUser () {
        // Don't pass on the arguments
        this.$root.$loadUser()
      },
      mailAnswer (value) {
        this.answered = true
        artCall('/api/profiles/v1/mailing-list-pref/', value, undefined, this.refreshUser)
      }
    },
    computed: {
      showMailingPrompt () {
        if (this.answered) {
          return true
        }
        if (this.viewer.username && !this.viewer.offered_mailchimp) {
          return true
        }
      },
      randomBanner () {
        // Lazy calculation, so should always match on a specific render.
        return this.banners[Math.floor(Math.random() * this.banners.length)]
      }
    }
  }
</script>
