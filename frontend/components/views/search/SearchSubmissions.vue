<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-flex xs4 sm3 lg2 v-for="submission in list.list" :key="submission.x.id">
      <ac-gallery-preview class="pa-1"
                          :submission="submission.x">
      </ac-gallery-preview>
    </v-flex>
    <v-flex text-xs-center slot="empty">
      <v-card>
        <v-card-text>
          We could not find anything which matched your request.
        </v-card-text>
      </v-card>
    </v-flex>
  </ac-paginated>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import Component, {mixins} from 'vue-class-component'
import Submission from '@/types/Submission'
import SearchList from '@/components/views/search/mixins/SearchList'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
  @Component({
    components: {AcGalleryPreview, AcPaginated},
  })
export default class SearchSubmissions extends mixins(SearchList) {
    public list: ListController<Submission> = null as unknown as ListController<Submission>
    public created() {
      this.list = this.$getList('searchSubmissions', {endpoint: '/api/profiles/v1/search/submission/'})
    }
}
</script>
