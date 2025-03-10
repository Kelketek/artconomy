<template>
  <ac-paginated
    :list="list"
    :track-pages="true"
    :auto-run="false"
  >
    <template #default>
      <v-col
        v-for="character in list.list"
        :key="character.x!.id"
        class="pa-2"
        sm="6"
        md="4"
        lg="3"
        xl="2"
      >
        <ac-character-preview :character="character.x!" />
      </v-col>
    </template>
    <template #empty>
      <v-col class="text-center">
        <v-card>
          <v-card-text>
            We could not find anything which matched your request.
          </v-card-text>
        </v-card>
      </v-col>
    </template>
  </ac-paginated>
</template>
<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {useSearchList} from '@/components/views/search/mixins/SearchList.ts'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {Character} from '@/store/characters/types/main'

const searchForm = useForm('search')
const list = useList<Character>('searchCharacters', {
  endpoint: '/api/profiles/search/character/',
  persistent: true,
})

useSearchList(searchForm, list)
</script>
