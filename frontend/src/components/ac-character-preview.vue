<template>
  <div class="col-12-sm col-4-md col-3-lg col-centered character-preview pr-2 pl-2 mb-3">
      <div class="card">
        <router-link :to="{name: 'Character', params: {username: character.user.username, character: character.name}}">
          <img v-if="character.primary_asset && character.primary_asset.id" class="card-img-top" :src="character.primary_asset.file" />
          <img v-else class="card-img-top" src="/static/images/default-avatar.png" />
        </router-link>
        <div class="bg-primary card-header character-name-tag fg-light">{{ character.name }}</div>
      </div>
  </div>
</template>

<script>
  export default {
    name: 'ac-character-preview',
    props: ['character']
  }
</script>
