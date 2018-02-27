<template>
  <v-flex v-bind="$attrs">
    <v-card class="character-card">
      <router-link :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
        <v-card-media
            :src="$img(character.primary_asset, 'thumbnail')"
        >
            <ac-asset
                :asset="character.primary_asset"
                thumb-name="thumbnail"
                :terse="true"
                :text-only="true"
            />
        </v-card-media>
      </router-link>
      <v-card-title>
          <router-link :to="{name: 'Character', params: {username: character.user.username, characterName: character.name}}">
            {{ character.name }}
          </router-link>
        <span v-if="removable" @click="remove"><v-icon>close</v-icon></span>
      </v-card-title>
    </v-card>
    <div class="showcase-button-container" v-if="canShowcase">
      <ac-action :url="url" variant="primary" :success="callback" :disabled="showcased">
        <span v-if="showcased" :button="true">Showcased</span>
        <span v-else>Showcase</span>
      </ac-action>
    </div>
  </v-flex>
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
