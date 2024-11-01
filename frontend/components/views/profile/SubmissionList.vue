<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <v-col cols="4" sm="3" lg="2" v-for="submission in derivedList" :key="submission.id">
      <ac-gallery-preview class="pa-1"
                          :submission="submission" :show-footer="false">
      </ac-gallery-preview>
    </v-col>
    <template v-slot:failure>
      <v-col class="text-center" v-if="okStatuses"><p>{{ failureMessage }}</p></v-col>
    </template>
    <template v-slot:empty>
      <v-col class="text-center" v-if="emptyMessage"><p>{{ emptyMessage }}</p></v-col>
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
    // @ts-expect-error
    if (single.x?.submission !== undefined) {
      // @ts-expect-error
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
