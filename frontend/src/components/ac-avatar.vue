<template>
  <div class="avatar-container">
    <router-link :to="{name: 'Profile', params: {username: user.username}}">
      <div class="shadowed avatar-image-container">
        <img :src="user.avatar_url">
      </div>
      <div class="avatar-username text-center">{{ user.username }}</div>
    </router-link>
  </div>
</template>


<script>
  export default {
    name: 'ac-avatar',
    props: ['user']
  }
</script>

<style>
  .avatar-container{
    display: inline-block;
  }
  .avatar-image-container {
    border: 1px solid black;
  }
  .avatar-username {
    font-weight: bold;
    margin-bottom: .5rem;
  }
</style>