<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <v-col cols="4" sm="3" lg="2" v-for="submission in derivedList" :key="submission.id">
      <ac-gallery-preview class="pa-1"
                          :submission="submission" :show-footer="false">
      </ac-gallery-preview>
    </v-col>
    <template v-slot:failure>
      <v-col class="text-center" v-if="okStatuses"><p>{{failureMessage}}</p></v-col>
    </template>
    <template v-slot:empty>
      <v-col class="text-center" v-if="emptyMessage"><p>{{emptyMessage}}</p></v-col>
    </template>
  </ac-paginated>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import Editable from '@/mixins/editable'
import ArtistTag from '@/types/ArtistTag'

@Component({
  components: {
    AcPaginated,
    AcGalleryPreview,
    AcLoadSection,
  },
})
class SubmissionList extends mixins(Subjective, Editable) {
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

  @Watch('rawRating')
  public refreshListing(newValue: Ratings, oldValue: Ratings | undefined) {
    if (oldValue === undefined) {
      return
    }
    this.list.get()
  }

  public get derivedList(): Submission[] {
    return this.list.list.map((single) => {
      // @ts-ignore
      if (single.x?.submission !== undefined) {
        // @ts-ignore
        return single.x.submission as Submission
      }
      return single.x as Submission
    })
  }

  public list = null as unknown as ListController<Submission | ArtistTag>

  public created() {
    let listName = this.listName
    if (this.username) {
      listName = `${flatten(this.username)}-${listName}`
    }
    this.list = this.$getList(listName, {endpoint: this.endpoint})
  }
}

export default toNative(SubmissionList)
</script>
