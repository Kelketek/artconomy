<template>
  <div class="container home">
    <div class="row">
      <div class="col-sm-12">
        <p>Welcome to Artconomy!</p>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'Home',
    created () {
      document.title = 'Artconomy-- Where artists and commissioners meet!'
      let desctag = document.head.querySelector('meta[name=description]')
      if (desctag) {
        // This can be absent in the test environment.
        desctag.content = 'Artconomy lets you find artists to draw your personal characters.'
      }
    }
  }
</script>
