<template>
  <div class="avatar-container">
      <div class="text-xs-center avatar-image-wrapper">
        <v-avatar v-if="noLink">
          <img :src="user.avatar_url">
        </v-avatar>
        <router-link v-else :to="{name: 'Profile', params: {username: this.user.username}}">
          <v-avatar>
            <img :src="user.avatar_url">
          </v-avatar>
        </router-link>
        <div v-if="showName" class="text-xs-center" :class="{'mb-2': !showRating}">
          <v-tooltip bottom v-if="user.is_superuser">
            <v-icon slot="activator" small class="green--text">stars</v-icon>
            <span>Admin</span>
          </v-tooltip>
          <v-tooltip bottom v-else-if="user.is_staff">
            <v-icon slot="activator" small class="yellow--text">stars</v-icon>
            <span>Staff</span>
          </v-tooltip>
          <!--<span v-else-if="user.is_staff"><v-icon small class="yellow&#45;&#45;text">stars</v-icon> Staff</span>-->
          <span v-if="noLink">{{user.username}}</span>
          <router-link :to="{name: 'Profile', params: {username: user.username}}" v-else>{{ user.username }}</router-link>
          <v-icon small v-if="removable" @click="remove">close</v-icon>
        </div>
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