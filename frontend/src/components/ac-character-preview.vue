<template>
  <div class="col-12-sm col-4-md col-3-lg col-centered character-preview pr-2 pl-2 mb-3">
      <div class="card character-card">
        <router-link :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
          <ac-asset :terse="true" thumb-name="thumbnail" v-if="character.primary_asset && character.primary_asset.id" :asset="character.primary_asset" img-class="card-img-top"></ac-asset>
          <img v-else class="card-img-top" src="/static/images/default-avatar.png" />
        </router-link>
        <div class="bg-primary card-header character-name-tag fg-light">{{ character.name }}</div>
      </div>
  </div>
</template>

<script>
  import AcAsset from './ac-asset'
  export default {
    components: {AcAsset},
    props: ['character']
  }
</script>
