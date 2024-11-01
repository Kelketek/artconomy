<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-row no-gutters>
      <v-col cols="4" sm="3" lg="2" v-for="submission in list.list" :key="submission.x!.id">
        <ac-gallery-preview :submission="submission.x!" :show-footer="false"/>
      </v-col>
    </v-row>
    <template v-slot:empty>
      <v-row no-gutters>
        <v-col class="text-center">
          <v-card>
            <v-card-text>
              We could not find anything which matched your request.
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-paginated>
</template>
<script setup lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {useSearchList} from '@/components/views/search/mixins/SearchList.ts'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'

import type {Submission} from '@/types/main'

const searchForm = useForm('search')

const list = useList<Submission>('searchSubmissions', {
  endpoint: '/api/profiles/search/submission/',
  persistent: true,
})
useSearchList(searchForm, list)
</script>
