<template>
  <div class="container home">
    <div class="intro" v-if="viewer !== null && !viewer.username">
      <div class="row">
        <div class="col-12 text-center">
          <img class="home-logo" src="/static/images/logo.svg"/>
        </div>
        <div class="col-12 text-center home-title">
          <h1>Welcome to Artconomy</h1>
        </div>
      </div>
      <div class="row">
        <div class="col-12 col-md-6 text-center">
          <h3>Upload and catalog your characters</h3>
          <p>Have a character you want to show off? Now you have the tools to do it, for free!</p>
        </div>
        <div class="col-12 col-md-6 text-center">
          <img class="demo-img" src="/static/images/characterbrowse.jpg" />
        </div>
        <div class="col-12 col-md-6 text-center">
          <h3>Commission Artists</h3>
          <p>Have a character in mind but need help bringing it to life? Have an artist make a reference sheet, and many more to stylize your characters as much as you please.</p>
          <p>See artists by rating and pricing, and commission with confidence.</p>
        </div>
        <div class="col-12 col-12 text-center">
          <h3>Are you an artist?</h3>
          <p>Get a free shop where people can commission you!</p>
          <p>Use built-in communications tools for helping clients keep track of your progress.</p>
          <p>Have the safety and assurance of contracts and escrow payments-- no more worrying about getting paid!</p>
        </div>
      </div>
    </div>
    <div class="home-main">
      <div class="row">
        <div class="col-12">
          <h2>Recent Submissions</h2>
        </div>
      </div>
      <ac-asset-gallery
          endpoint="/api/profiles/v1/recent-submissions/" :limit="4"
      />
      <div class="row">
        <div class="col-12">
          <h2>Recent Commissions</h2>
        </div>
      </div>
      <ac-asset-gallery
          endpoint="/api/profiles/v1/recent-commissions/" :limit="4"
      />
      <div class="row">
        <div class="col-12">
          <h2>New Characters</h2>
        </div>
      </div>
      <characters
          endpoint="/api/profiles/v1/new-characters/" :limit="4"
      />
    </div>
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
    width: 100%;
  }
</style>

<script>
  import { setMetaContent } from '../lib'
  import AcAssetGallery from './ac-asset-gallery'
  import Characters from './Characters'

  export default {
    components: {
      Characters,
      AcAssetGallery},
    name: 'Home',
    created () {
      document.title = 'Artconomy-- Where artists and commissioners meet!'
      setMetaContent('description', 'Artconomy lets you find artists to draw your personal characters.')
    }
  }
</script>
