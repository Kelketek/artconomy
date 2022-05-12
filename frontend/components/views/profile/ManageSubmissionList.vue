<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <draggable tag="v-row" :component-data="{'no-gutters': true}" v-model="sortableList">
      <v-col cols="4" sm="3" lg="2" v-for="submission in sortableList" :key="submission.x.id">
        <ac-gallery-preview class="pa-1"
                            :submission="submission.x" :show-footer="false">
        </ac-gallery-preview>
      </v-col>
    </draggable>
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
import {Prop, Watch} from 'vue-property-decorator'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import Editable from '@/mixins/editable'
import draggable from 'vuedraggable'
import diff from 'list-diff.js'

@Component({
  components: {
    AcPaginated,
    AcGalleryPreview,
    AcLoadSection,
    draggable,
  },
})
export default class ManageSubmissionList extends mixins(Subjective, Editable) {
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
    public refreshListing(newValue: Ratings, oldValue: Ratings|undefined) {
      if (oldValue === undefined) {
        return
      }
      this.list.get()
    }

    public get sortableList() {
      const list = [...this.list.list]
      list.sort((a, b) => -(a.patchers.display_position.model - b.patchers.display_position.model))
      console.log(list.map((controller) => [controller.x!.id, controller.x!.display_position]))
      return list
    }

    public set sortableList(newVersion) {
      // This function should only be used by vue-draggable. It is not a general purpose way to modify the list.
      // Doing anything else with it is liable to break things.
      //
      // Need to find the difference here.
      const a = this.sortableList.map((controller) => controller.x!.id)
      const b = newVersion.map((controller) => controller.x!.id)
      const moves = diff(a, b)
      // Nothing has changed.
      if (moves.length === 0) {
        return
      }
      // This is the insertion move. It tells us the target index where our resulting item was inserted.
      const move = moves.filter((move) => move.type === 1)[0]
      let index = move.index
      // If we delete after the fact, it means that our target index will shift downward. The algorithm only deletes
      // afterward in cases where our index will shift down-- it doesn't do it when moving us toward the beginning,
      // but to the end.
      if (moves[1].type === 0) {
        index -= 1
      }
      const target = newVersion[index]
      if (index === 0) {
        // There must be one other entry or else the drag-and-drop would create no difference.
        //
        // However we really need to know the on-server 'up' value on this one to do this right.
        // TODO: Replace this with an 'up' call, server-side.
        target.patchers.display_position.model = newVersion[1].patchers.display_position.model + 1
        return
      }
      if (index === (newVersion.length - 1)) {
        // TODO: Replace this with a 'down' call, server-side.
        target.patchers.display_position.model = (newVersion[index - 1].patchers.display_position.model - 1)
        return
      }
      // Averaging what's in front and behind will set this item's position between.
      target.patchers.display_position.model = (
        newVersion[index - 1].patchers.display_position.model +
        newVersion[index + 1].patchers.display_position.model
      ) / 2
    }

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
