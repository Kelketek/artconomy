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
  import { setMetaContent } from '../lib'

  export default {
    name: 'Home',
    created () {
      document.title = 'Artconomy-- Where artists and commissioners meet!'
      setMetaContent('description', 'Artconomy lets you find artists to draw your personal characters.')
    }
  }
</script>
