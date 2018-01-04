<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-12">
        <p>{{ user.username }}'s profile.</p>
      </div>
    </div>
    <div class="row shadowed">
      <div class="col-sm-12 text-section pt-2 mb-2">
        <h2>Characters</h2>
      </div>
      <Characters :username="username" embedded="true" :limit="5"></Characters>
    </div>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Characters from './Characters'

  export default {
    name: 'Profile',
    mixins: [Viewer, Perms],
    components: {Characters},
    data: function () {
      return {
        user: {username: this.$route.params['username']}
      }
    },
    computed: {
      controls: function () {
        return this.$root.user.is_staff || (this.user.username === this.$root.user.username)
      }
    }
  }
</script>
