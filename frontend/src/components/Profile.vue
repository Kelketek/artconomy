<template>
  <div class="container">
    <div class="row shadowed">
      <div class="col-2 text-section pt-2">
        <ac-avatar :user="user" />
      </div>
      <div class="text-section col-7 pt-2">
        <h3>About {{user.username}}</h3>
        <ac-patchfield
            v-model="user.biography"
            name="biography"
            :multiline="true"
            :editmode="controls"
            :url="url"
            placeholder="Write a bit about yourself!"
        />
      </div>
      <div class="col-3 text-section pt-2">

      </div>
    </div>
    <div class="row shadowed pb-2">
      <div class="col-12 text-section pt-2 mb-2">
        <h2>Characters</h2>
      </div>
      <Characters
          :username="username"
          embedded="true"
          :limit="5"
          :endpoint="`/api/profiles/v1/account/${username}/characters/`" />
    </div>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import Characters from './Characters'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'

  export default {
    name: 'Profile',
    mixins: [Viewer, Perms],
    components: {
      AcPatchfield,
      AcAvatar,
      Characters,
      Editable
    },
    data: function () {
      return {
        user: {username: this.username},
        url: `/api/profiles/v1/data/user/${this.username}/`
      }
    },
    computed: {
      controls: function () {
        return this.$root.user.is_staff || (this.user.username === this.$root.user.username)
      }
    }
  }
</script>
