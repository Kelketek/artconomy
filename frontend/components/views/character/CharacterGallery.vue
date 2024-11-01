<template>
  <v-container fluid>
    <ac-load-section :controller="character.profile">
      <ac-character-toolbar :username="username" :character-name="characterName"
                            @success="character.submissions.unshift" :visit="false"/>
      <ac-paginated :list="character.submissions" :track-pages="true" class="pt-3">
        <v-col cols="4" sm="3" lg="2" v-for="submission in character.submissions.list" :key="submission.x!.id">
          <ac-gallery-preview class="pa-1" :submission="submission.x!"/>
        </v-col>
      </ac-paginated>
    </ac-load-section>
  </v-container>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {useRatingRefresh} from '@/mixins/RatingRefresh.ts'
import {useCharacter} from '@/store/characters/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import type {CharacterProps} from '@/types/main'

const props = defineProps<CharacterProps>()
const character = useCharacter(props)
const {setError} = useErrorHandling()
character.profile.get().catch(setError)
character.submissions.firstRun().catch(setError)

useRatingRefresh([character.submissions])
</script>
