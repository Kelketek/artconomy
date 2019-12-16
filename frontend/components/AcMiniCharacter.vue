<template>
  <div class="shrink text-center flex">
    <div class="flex">
      <div class="flex">
        <router-link :to="route">
          <v-avatar :color="$vuetify.theme.currentTheme.darkBase.darken4">
            <v-icon v-if="!canDisplay">block</v-icon>
            <img :src="displayImage" v-else-if="canDisplay && displayImage" class="asset-image" alt="">
          </v-avatar>
        </router-link>
      </div>
      <div v-if="showName" class="flex text-center">
        <router-link :to="route">{{ character.name }}</router-link>
      </div>
      <div class="flex" v-if="removable">
        <v-btn small icon color="danger" @click="$emit('remove')"><v-icon small>close</v-icon></v-btn>
      </div>
    </div>
  </div>
</template>

<style>
  /*noinspection CssUnusedSymbol*/
  .ac-avatar .v-rating.v-rating--dense .v-icon {
    padding: 0.025rem;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AssetBase from '@/mixins/asset_base'
import {Prop} from 'vue-property-decorator'
import {Character} from '@/store/characters/types/Character'
import {Asset} from '@/types/Asset'
import {getExt} from '@/lib'

  @Component
export default class AcMiniCharacter extends mixins(AssetBase) {
    @Prop({required: true})
    public character!: Character
    @Prop({default: true})
    public showName!: boolean
    @Prop({default: false})
    public removable!: boolean
    public thumbName = 'thumbnail'
    public get asset() {
      return this.character.primary_submission as Asset
    }
    public get route() {
      return {name: 'Character', params: {username: this.character.user.username, characterName: this.character.name}}
    }
}
</script>
