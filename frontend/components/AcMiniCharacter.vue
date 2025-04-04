<template>
  <div class="shrink text-center d-inline-flex">
    <div class="flex">
      <div class="flex">
        <router-link :to="route">
          <v-avatar :color="current.colors.well">
            <v-icon v-if="!canDisplay" :icon="mdiCancel" />
            <img
              v-else-if="canDisplay && displayImage"
              :src="displayImage"
              class="asset-image"
              :alt="alt"
            />
          </v-avatar>
        </router-link>
      </div>
      <div v-if="showName" class="flex text-center">
        <router-link :to="route">
          {{ character.name }}
        </router-link>
      </div>
      <div v-if="removable" class="flex">
        <v-btn size="x-small" icon color="danger" @click="emit('remove')">
          <v-icon size="large" :icon="mdiClose" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { assetDefaults, useAssetHelpers } from "@/mixins/asset_base.ts"
import { computed } from "vue"
import { mdiCancel, mdiClose } from "@mdi/js"
import { useTheme } from "vuetify"
import type { AssetProps } from "@/types/main"
import { Character } from "@/store/characters/types/main"

declare interface AcMiniCharacterProps extends AssetProps {
  character: Character
  showName?: boolean
  removable?: boolean
}

const { current } = useTheme()

const props = withDefaults(defineProps<AcMiniCharacterProps>(), {
  ...assetDefaults(),
  showName: true,
  removable: false,
})

const asset = computed(() => props.character.primary_submission)

const emit = defineEmits<{ remove: [] }>()

const { canDisplay, displayImage } = useAssetHelpers({
  asset: asset.value,
  thumbName: "thumbnail",
  fallbackImage: props.fallbackImage,
})

const route = computed(() => ({
  name: "Character",
  params: {
    username: props.character.user.username,
    characterName: props.character.name,
  },
}))
</script>

<style>
/*noinspection CssUnusedSymbol*/
.ac-avatar .v-rating.v-rating--dense .v-icon {
  padding: 0.025rem;
}
</style>
