<template>
  <div class="col-12-sm col-4-md col-3-lg col-centered character-preview pr-2 pl-2 mb-3 clickable">
    <div class="card character-card">
      <div class="bg-primary card-header character-name-tag fg-light">
        {{ character.name }}
        <span v-if="removable" @click="remove"><i class="fa fa-times"></i></span>
      </div>
      <router-link :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
        <ac-asset
            :terse="true"
            thumb-name="thumbnail"
            v-if="character.primary_asset && character.primary_asset.id"
            :asset="character.primary_asset"
            img-class="card-img-top"
        />
        <img v-else class="card-img-top" src="/static/images/default-avatar.png" />
      </router-link>
    </div>
    <div class="showcase-button-container" v-if="canShowcase">
      <ac-action :url="url" variant="primary" :success="callback" :disabled="showcased">
        <span v-if="showcased" :button="true">Showcased</span>
        <span v-else>Showcase</span>
      </ac-action>
    </div>
  </div>
</template>

<style>
  .card-header.character-name-tag {
    position: absolute;
    bottom: 0;
    max-width: 75%;
    max-height: 3em;
    opacity: .75;
    overflow: hidden;
    white-space:nowrap;
    transition: max-width .25s, width .25s, opacity .25s;
    z-index: 3;
  }

  .showcase-button-container {
    text-align: center
  }

  .character-preview .card-img-top {
    object-fit: cover;
    height: 15rem;
    width: 15rem;
    object-position: center top;
    z-index: 0;
  }

  .character-preview:hover .character-name-tag {
    max-width: 100%;
    width: 100%;
    opacity: 1;
    transition: max-width .25s, width .25s, opacity .25s;
    z-index: 3;
  }
</style>

<script>
  import AcAsset from './ac-asset'
  import { artCall } from '../lib'
  import AcAction from './ac-action'
  export default {
    name: 'ac-character-preview',
    components: {
      AcAction,
      AcAsset},
    methods: {
      remove () {
        artCall(this.removeUrl, 'DELETE', {'characters': [this.character.id]}, this.callback)
      }
    },
    props: {
      character: {},
      removable: {
        default: false
      },
      removeUrl: {},
      callback: {
        default: function () {}
      },
      // ID of zero evaluates to false and is not valid ID number for our DB.
      canShowcase: {
        default: false
      },
      assetId: {
        default: 0
      }
    },
    computed: {
      url () {
        return `/api/profiles/v1/account/${this.character.user.username}/characters/${this.character.name}/asset/primary/${this.assetId}/`
      },
      showcased () {
        return this.character.primary_asset && (this.character.primary_asset.id === this.assetId)
      }
    }
  }
</script>
