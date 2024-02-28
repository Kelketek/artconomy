<template>
  <div class="shrink text-center d-inline-flex">
    <div class="flex">
      <div class="flex">
        <router-link :to="route">
          <v-avatar :color="$vuetify.theme.current.colors.well">
            <v-icon v-if="!canDisplay" icon="mdi-cancel"/>
            <img :src="displayImage" v-else-if="canDisplay && displayImage" class="asset-image" :alt="alt">
          </v-avatar>
        </router-link>
      </div>
      <div v-if="showName" class="flex text-center">
        <router-link :to="route">{{ character.name }}</router-link>
      </div>
      <div class="flex" v-if="removable">
        <v-btn size="x-small" icon color="danger" @click="emit('remove')">
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

<script setup lang="ts">
import {assetDefaults, useAssetHelpers} from '@/mixins/asset_base.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AssetProps from '@/types/AssetProps.ts'
import {computed} from 'vue'

declare interface AcMiniCharacterProps extends AssetProps {
  character: Character,
  showName?: boolean,
  removable?: boolean
}

const props = withDefaults(
    defineProps<AcMiniCharacterProps>(),
    {
      ...assetDefaults(),
      showName: true,
      removable: false,
    },
)

const asset = computed(() => props.character.primary_submission)

const emit = defineEmits<{ remove: [] }>()

const {
  canDisplay,
  displayImage,
} = useAssetHelpers({
  asset: asset.value,
  thumbName: 'thumbnail',
  fallbackImage: props.fallbackImage,
})

const route = computed(() => ({
  name: 'Character',
  params: {
    username: props.character.user.username,
    characterName: props.character.name,
  },
}))
</script>
