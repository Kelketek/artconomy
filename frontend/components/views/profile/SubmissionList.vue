<template>
  <ac-paginated
    :list="list"
    :track-pages="trackPages"
    :ok-statuses="okStatuses"
    :show-pagination="showPagination"
  >
    <v-col
      v-for="submission in derivedList"
      :key="submission.id"
      cols="4"
      sm="3"
      lg="2"
    >
      <ac-gallery-preview
        class="pa-1"
        :submission="submission"
        :show-footer="false"
      />
    </v-col>
    <template #failure>
      <v-col
        v-if="okStatuses"
        class="text-center"
      >
        <p>{{ failureMessage }}</p>
      </v-col>
    </template>
    <template #empty>
      <v-col
        v-if="emptyMessage"
        class="text-center"
      >
        <p>{{ emptyMessage }}</p>
      </v-col>
    </template>
  </ac-paginated>
</template>

<script setup lang="ts">
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, watch} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import type {ArtistTag, SubjectiveProps, Submission} from '@/types/main'

declare interface SubmissionListProps extends SubjectiveProps {
  listName: string,
  endpoint: string,
  emptyMessage?: string,
  failureMessage?: string,
  trackPages?: boolean,
  showPagination?: boolean,
  okStatuses?: number[],
}

const props = withDefaults(defineProps<SubmissionListProps>(), {
  okStatuses: () => [],
  failureMessage: 'This content is disabled or unavailable.',
  emptyMessage: '',
  showPagination: true,
})

let listName = props.listName
if (props.username) {
  listName = `${flatten(props.username)}-${listName}`
}
const list = useList<Submission | ArtistTag>(listName, {endpoint: props.endpoint})

const derivedList = computed((): Submission[] => {
  return list.list.map((single) => {
    // @ts-expect-error Undefined check intentional here.
    if (single.x?.submission !== undefined) {
      // @ts-expect-error ditto.
      return single.x.submission as Submission
    }
    return single.x as Submission
  })
})

const {rawRating} = useViewer()

watch(rawRating, (newValue, oldValue) => {
  if (oldValue === undefined) {
    return
  }
  list.get()
})
</script>
