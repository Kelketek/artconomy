<template>
  <div class="avatar-container">
      <div class="text-center avatar-image-wrapper">
        <router-link :to="{name: 'Profile', params: {username: user.username}}">
          <div class="shadowed avatar-image-container">
            <img :src="user.avatar_url">
          </div>
        </router-link>
      </div>
    <div class="avatar-username text-center"><router-link :to="{name: 'Profile', params: {username: user.username}}">{{ user.username }}</router-link> <span v-if="removable" @click="remove"><i class="fa fa-times"></i></span></div>
  </div>
</template>


<script>
  import { artCall } from '../lib'

  export default {
    name: 'ac-avatar',
    props: {
      user: {},
      removable: {
        default: false
      },
      fieldName: {},
      removeUrl: {},
      callback: {
        default: function () {}
      }
    },
    methods: {
      remove () {
        let data = {}
        data[this.fieldName] = [this.user.id]
        artCall(this.removeUrl, 'DELETE', data, this.callback)
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
    margin-bottom: .5rem;
  }
</style>