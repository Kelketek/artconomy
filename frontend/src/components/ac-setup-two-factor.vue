<template>
  <div class="container">
    <div class="row">
      Test
    </div>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  export default {
    mixins: [Viewer, Perms],
    name: 'ac-setup-two-factor'
  }
</script>