<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <v-col cols="4" sm="3" lg="2" v-for="submission in list.list" :key="submission.x.id">
      <ac-gallery-preview class="pa-1"
                          :submission="submission.x" :show-footer="false">
      </ac-gallery-preview>
    </v-col>
    <v-col class="text-center" slot="failure" v-if="okStatuses"><p>{{failureMessage}}</p></v-col>
    <v-col class="text-center" slot="empty" v-if="emptyMessage"><p>{{emptyMessage}}</p></v-col>
  </ac-paginated>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import {Prop} from 'vue-property-decorator'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib'
  @Component({
    components: {AcPaginated, AcGalleryPreview, AcLoadSection},
  })
export default class SubmissionList extends mixins(Subjective) {
    @Prop()
    public listName!: string

    @Prop()
    public endpoint!: string

    @Prop({default: false})
    public trackPages!: false

    @Prop({default: () => []})
    public okStatuses!: number[]

    @Prop({default: 'This content is disabled or unavailable.'})
    public failureMessage!: string

    @Prop({default: ''})
    public emptyMessage!: string

    @Prop({default: true})
    public showPagination!: boolean

    public list: ListController<Submission> = null as unknown as ListController<Submission>
    public created() {
      let listName = this.listName
      if (this.username) {
        listName = `${flatten(this.username)}-${listName}`
      }
      this.list = this.$getList(listName, {endpoint: this.endpoint})
    }
}
</script>
