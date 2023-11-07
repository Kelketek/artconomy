<template>
  <div class="shrink text-center d-inline-flex">
    <div class="flex">
      <div class="flex">
        <router-link :to="route">
          <v-avatar :color="$vuetify.theme.current.colors.well">
            <v-icon v-if="!canDisplay" icon="mdi-cancel"/>
            <img :src="displayImage" v-else-if="canDisplay && displayImage" class="asset-image" alt="">
          </v-avatar>
        </router-link>
      </div>
      <div v-if="showName" class="flex text-center">
        <router-link :to="route">{{ character.name }}</router-link>
      </div>
      <div class="flex" v-if="removable">
        <v-btn size="x-small" icon color="danger" @click="$emit('remove')">
          <v-icon size="large" icon="mdi-close"/>
        </v-btn>
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
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AssetBase from '@/mixins/asset_base'
import {Character} from '@/store/characters/types/Character'
import {Asset} from '@/types/Asset'

@Component({emits: ['remove']})
class AcMiniCharacter extends mixins(AssetBase) {
  @Prop({required: true})
  public character!: Character

  @Prop({default: true})
  public showName!: boolean

  @Prop({default: false})
  public removable!: boolean

  public thumbName = 'thumbnail'

  // @ts-ignore
  public get asset() {
    return this.character.primary_submission as Asset
  }

  public get route() {
    return {name: 'Character',
      params: {
        username: this.character.user.username,
        characterName: this.character.name,
      },
    }
  }
}

export default toNative(AcMiniCharacter)
</script>
