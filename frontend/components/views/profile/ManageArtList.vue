<template>
  <v-row no-gutters>
    <v-col cols="12">
      <v-card-text class="text-center">
        Click (or tap) and drag to rearrange your submissions. Drag onto the 'next' or
        'previous' button to put the submission before or after to shift them into the
        next or previous page. When you are finished, tap the 'finish' button.
      </v-card-text>
    </v-col>
    <v-col cols="12">
      <ac-draggable-list :list="list">
        <template v-slot:default="{element, index}">
          <v-col cols="4" sm="3" lg="2" :key="index" class="draggable-item">
            <artist-tag-manager :tag="element" :username="username" :key="index"/>
          </v-col>
        </template>
      </ac-draggable-list>
    </v-col>
  </v-row>
</template>

<style>
.disabled {
  opacity: .5;
}

.page-setter .sortable-ghost {
  display: none;
}

.page-setter .sortable-ghost + .v-card {
  filter: brightness(200%);
}

.page-setter .sortable-ghost + .v-card.disabled {
  filter: brightness(100%);
}

.unavailable {
  opacity: .5;
}
</style>

<script setup lang="ts">
import {flatten} from '@/lib/lib.ts'
import AcDraggableList from '@/components/AcDraggableList.vue'
import ArtistTag from '@/types/ArtistTag.ts'
import ArtistTagManager from '@/components/views/profile/ArtistTagManager.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useList} from '@/store/lists/hooks.ts'

const props = defineProps<SubjectiveProps & {listName: string, endpoint: string}>()
let listName = props.listName
if (props.username) {
  listName = `${flatten(props.username)}-${listName}-management`
}
const list = useList<ArtistTag>(listName, {endpoint: props.endpoint})
list.firstRun()
</script>
