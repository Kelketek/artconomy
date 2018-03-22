<template>
  <v-container>
    <v-card>
      <v-layout row wrap class="mb-4">
        <v-flex xs12 sm2  text-xs-center text-sm-left class="pt-2">
          <ac-avatar :user="user" />
        </v-flex>
        <v-flex xs12 sm10 class="pt-2 pl-2 pr-2">
          <h3>About {{user.username}}</h3>
          <ac-patchfield
              v-model="user.biography"
              name="biography"
              :multiline="true"
              :editmode="controls"
              :url="url"
              placeholder="Write a bit about yourself!"
          />
        </v-flex>
        <v-flex sm3 class="hidden-sm-and-down">
        </v-flex>
      </v-layout>
    </v-card>
    <ac-context-gallery
        :to="{name: 'Gallery', params: {username}}"
        :assets="assets"
        :total-pieces="count"
        see-more-text="View full gallery"
        v-if="assets && assets.length"
        class="mb-2"
    />
    <v-card>
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>Characters</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <Characters
        :username="username"
        embedded="true"
        :limit="5"
        :endpoint="`/api/profiles/v1/account/${username}/characters/`" />
    <v-card>
      <v-layout row wrap>
        <v-flex xs12 class="pl-2">
          <h2>Favorites</h2>
        </v-flex>
      </v-layout>
    </v-card>
    <ac-asset-gallery
        :endpoint="`/api/profiles/v1/account/${username}/favorites/`"
        :no-pagination="true"
        :to="{name: 'Gallery', params: {username}}"
        see-more-text="See all favorites"
    />
  </v-container>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Editable from '../mixins/editable'
  import Characters from './Characters'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'
  import AcAssetGallery from './ac-asset-gallery'
  import { artCall } from '../lib'
  import AcContextGallery from './ac-context-gallery'

  export default {
    name: 'Profile',
    mixins: [Viewer, Perms],
    components: {
      AcContextGallery,
      AcAssetGallery,
      AcPatchfield,
      AcAvatar,
      Characters,
      Editable
    },
    data: function () {
      return {
        user: {username: this.username},
        url: `/api/profiles/v1/data/user/${this.username}/`,
        count: 0,
        assets: null
      }
    },
    methods: {
      populateGallery (response) {
        this.assets = response.results
        this.count = response.count
      }
    },
    computed: {
      controls: function () {
        return this.$root.user.is_staff || (this.user.username === this.$root.user.username)
      }
    },
    created () {
      artCall(`/api/profiles/v1/account/${this.username}/gallery/`, 'GET', undefined, this.populateGallery)
    }
  }
</script>
