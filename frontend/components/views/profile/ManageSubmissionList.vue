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
          <v-col cols="4" sm="3" lg="2" :key="index">
            <ac-gallery-preview
                class="pa-1"
                @click.capture.stop.prevent="() => false"
                :linked="false"
                :key="index"
                :submission="element.x"
                :show-footer="true"
            />
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
</style>

<script setup lang="ts">
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {flatten} from '@/lib/lib.ts'
import {Ratings} from '@/types/Ratings.ts'
import AcDraggableList from '@/components/AcDraggableList.vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {watch} from 'vue'
import {useList} from '@/store/lists/hooks.ts'
import LinkedSubmission from '@/types/LinkedSubmission'

const props = defineProps<{listName: string, endpoint: string} & SubjectiveProps>()

const {rawRating} = useViewer()

let listName = props.listName
if (props.username) {
  listName = `${flatten(props.username)}-${listName}-management`
}

const list = useList<LinkedSubmission>(listName, {endpoint: props.endpoint})

watch(rawRating, (newValue: Ratings|undefined, oldValue: Ratings | undefined) => {
  if (oldValue === undefined || newValue === undefined) {
    return
  }
  list.get()
})
</script>
