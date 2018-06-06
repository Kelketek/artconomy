<template>
  <div class="avatar-container">
      <div class="text-xs-center avatar-image-wrapper">
        <router-link :to="link">
          <v-avatar>
            <img :src="user.avatar_url">
          </v-avatar>
        </router-link>
        <div v-if="showName" class="text-xs-center" :class="{'mb-2': !showRating}"><router-link :to="{name: 'Profile', params: {username: user.username}}">{{ user.username }}</router-link> <v-icon small v-if="removable" @click="remove">close</v-icon></div>
        <router-link :to="{name: 'Ratings', params: {username: user.username}}" v-if="showRating && user.stars">
          <ac-rating :value="user.stars" :small="true" class="mb-2 highlight-icon" />
        </router-link>
      </div>
  </div>
</template>


<script>
  import { artCall } from '../lib'
  import AcRating from './ac-rating'

  export default {
    name: 'ac-avatar',
    components: {AcRating},
    props: {
      user: {},
      removable: {
        default: false
      },
      showName: {default: true},
      fieldName: {},
      removeUrl: {},
      callback: {
        default: function () {}
      },
      showRating: {},
      noLink: {}
    },
    methods: {
      remove () {
        let data = {}
        data[this.fieldName] = [this.user.id]
        artCall(this.removeUrl, 'DELETE', data, this.callback)
      }
    },
    computed: {
      link () {
        if (this.noLink) {
          return {}
        }
        return {name: 'Profile', params: {username: this.user.username}}
      }
    }
  }
</script>

<style>
  .avatar-container{
    display: inline-block;
    line-height: 1.5rem;
  }
  .avatar-image-wrapper {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .avatar-image-container {
    border: 1px solid black;
    display: inline-block;
  }
  .avatar-username {
    font-weight: bold;
  }
</style>