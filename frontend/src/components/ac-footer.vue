<template>
  <footer id="footer">
    <b-navbar toggleable type="dark" variant="primary">
      <b-collapse is-nav id="footer_collapse">
        <b-navbar-nav class="ml-auto">
          <b-nav-item :to="{name: 'Policies'}">Legal/Policies</b-nav-item>
          <b-nav-item :to="{name: 'Contact'}">Contact</b-nav-item>
          <b-nav-item href="https://www.facebook.com/ArtconomyArt/"><i class="fa fa-facebook white-text"> </i></b-nav-item>
          <b-nav-item href="https://twitter.com/ArtconomyArt"><i class="fa fa-twitter white-text"> </i></b-nav-item>
        </b-navbar-nav>
      </b-collapse>
      <b-navbar-toggle target="footer_collapse"></b-navbar-toggle>
      <b-navbar-brand to="/"><img src="/static/images/logo.svg" class="header-logo"/><div class="logo-header-text">rtconomy</div></b-navbar-brand>
    </b-navbar>
  </footer>
</template>

<style>
  .white-text {
    color: #ffffff;
  }
  #footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    z-index: 10;
  }
</style>

<script>
  export default {
    name: 'ac-footer'
  }
</script>