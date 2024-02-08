<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-row no-gutters>
      <v-col cols="4" sm="3" lg="2" v-for="submission in list.list" :key="submission.x!.id">
        <ac-gallery-preview :submission="submission.x" :show-footer="false"/>
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
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller.ts'
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Submission from '@/types/Submission.ts'
import SearchList from '@/components/views/search/mixins/SearchList.ts'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'

@Component({
  components: {
    AcGalleryPreview,
    AcPaginated,
  },
  mixins: [],
})
class SearchSubmissions extends mixins(SearchList) {
  public list: ListController<Submission> = null as unknown as ListController<Submission>

  public created() {
    this.list = this.$getList('searchSubmissions', {
      endpoint: '/api/profiles/search/submission/',
      persistent: true,
    })
  }
}

export default toNative(SearchSubmissions)
</script>
