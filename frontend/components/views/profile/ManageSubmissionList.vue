<template>
  <v-row no-gutters>
    <v-col cols="12">
      <v-card-text class="text-center">
        Click (or tap) and drag to rearrange your submissions. Drag onto the
        'next' or 'previous' button to put the submission before or after to
        shift them into the next or previous page. When you are finished, tap
        the 'finish' button.
      </v-card-text>
    </v-col>
    <v-col cols="12">
      <ac-draggable-list :list="list">
        <template #default="{ element, index }">
          <v-col :key="index" cols="4" sm="3" lg="2">
            <ac-gallery-preview
              :key="index"
              class="pa-1"
              :linked="false"
              :submission="element.x"
              :show-footer="true"
              @click.capture.stop.prevent="() => false"
            />
          </v-col>
        </template>
      </ac-draggable-list>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import { flatten } from "@/lib/lib.ts"
import AcDraggableList from "@/components/AcDraggableList.vue"
import { useViewer } from "@/mixins/viewer.ts"
import { watch } from "vue"
import { useList } from "@/store/lists/hooks.ts"

import type {
  LinkedSubmission,
  RatingsValue,
  SubjectiveProps,
} from "@/types/main"

const props = defineProps<
  { listName: string; endpoint: string } & SubjectiveProps
>()

const { rawRating } = useViewer()

let listName = props.listName
if (props.username) {
  listName = `${flatten(props.username)}-${listName}-management`
}

const list = useList<LinkedSubmission>(listName, { endpoint: props.endpoint })

watch(
  rawRating,
  (newValue: RatingsValue | undefined, oldValue: RatingsValue | undefined) => {
    if (oldValue === undefined || newValue === undefined) {
      return
    }
    list.get()
  },
)
</script>

<style>
.disabled {
  opacity: 0.5;
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
