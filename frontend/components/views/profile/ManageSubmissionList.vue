<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <v-col cols="12">
      <v-row no-gutters>
        <draggable
            tag="v-col"
            :component-data="{cols: 6}"
            :list="previousList"
            :group="{name: 'previous', put: () => true, pull: false, draggable: '.dropitem'}"
            class="page-setter"
            @add="addPrevious"
        >
          <template v-slot:header>
            <v-card :class="{disabled: list.currentPage === 1}">
              <v-card-text class="text-center">
                Previous
              </v-card-text>
            </v-card>
          </template>
        </draggable>
        <draggable
            tag="v-col"
            :component-data="{cols: 6}"
            :list="nextList"
            :group="{name: 'next', put: () => true, pull: false, draggable: '.dropitem'}"
            class="page-setter"
            @add="addNext"
        >
          <template v-slot:header>
            <v-card :class="{disabled: list.currentPage === list.totalPages}">
              <v-card-text class="text-center">
                Next
              </v-card-text>
            </v-card>
          </template>
        </draggable>
      </v-row>
      <v-col cols="12" class="py-2"></v-col>
    </v-col>
    <v-col cols="12">
      <draggable tag="v-row" :component-data="{'no-gutters': true}" v-model="sortableList" :group="{name: 'main', put: false, pull: 'clone'}">
        <v-col cols="4" sm="3" lg="2" v-for="submission in sortableList" :key="submission.x.id">
          <ac-gallery-preview class="pa-1"
                              :submission="submission.x" :show-footer="false">
          </ac-gallery-preview>
        </v-col>
      </draggable>
    </v-col>
    <v-col class="text-center" slot="failure" v-if="okStatuses"><p>{{failureMessage}}</p></v-col>
    <v-col class="text-center" slot="empty" v-if="emptyMessage"><p>{{emptyMessage}}</p></v-col>
  </ac-paginated>
</template>

<style scoped>
.disabled {
  opacity: .5;
}
.page-setter .sortable-ghost {
  display: none;
}
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {ListController} from '@/store/lists/controller'
import Submission from '@/types/Submission'
import {Prop, Watch} from 'vue-property-decorator'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {artCall, flatten} from '@/lib/lib'
import {Ratings} from '@/store/profiles/types/Ratings'
import Editable from '@/mixins/editable'
import draggable from 'vuedraggable'
import diff, {DiffPatch} from 'list-diff.js'

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

    public get previousList() {
      return []
    }

    public get nextList() {
      return []
    }

    public addNext(addEvent: any) {
      this.adder(addEvent, false)
    }

    public addPrevious(addEvent: any) {
      if (this.list.currentPage === 1) {
        return
      }
      this.adder(addEvent, true)
    }

    public adder(addEvent: any, previous: boolean) {
      const controller = this.sortableList[addEvent.oldDraggableIndex]
      let borderIndex: number
      let suffix: string
      if (previous) {
        suffix = 'up'
        borderIndex = 0
      } else {
        suffix = 'down'
        borderIndex = this.sortableList.length - 1
      }
      const borderController = this.sortableList[borderIndex]
      artCall({url: `${controller.endpoint}${suffix}/`, method: 'post', data: {current_value: borderController.x!.display_position}}).catch(() => {
        if (controller.purged) {
          return
        }
        controller.deleted = false
      })
      controller.deleted = true
    }

    public get sortableList() {
      const list = [...this.list.list]
      list.sort((a, b) => -(a.patchers.display_position.model - b.patchers.display_position.model))
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
      let index: number
      let move: DiffPatch<number>
      if (moves.length === 1 && moves[0].type === 0) {
        move = moves[0]
        this.sortableList[move.index].deleted = true
        return
      }
      // This is the insertion move. It tells us the target index where our resulting item was inserted.
      move = moves.filter((move) => move.type === 1)[0]
      index = move.index
      // If we delete after the fact, it means that our target index will shift downward. The algorithm only deletes
      // afterward in cases where our index will shift down-- it doesn't do it when moving us toward the beginning,
      // but to the end.
      if (moves[1].type === 0) {
        index -= 1
      }
      const setPosition = (response: Submission) => {
        target.setX(response)
        target.patchers.display_position.model = response.display_position
      }
      const target = newVersion[index]
      if (index === 0) {
        // There must be one other entry or else the drag-and-drop would create no difference.
        //
        // However we really need to know the on-server 'up' value on this one to do this right.
        // TODO: Replace this with an 'up' call, server-side.
        const first = this.sortableList[index]
        target.updateX({display_position: first.patchers.display_position.model + 0.1})
        artCall({url: `${target.endpoint}up/`, method: 'post', data: {relative_to: first.x!.id}}).then(setPosition)
        return
      }
      if (index === (newVersion.length - 1)) {
        const last = this.sortableList[index]
        target.updateX({display_position: last.patchers.display_position.model - 0.1})
        artCall({url: `${target.endpoint}down/`, method: 'post', data: {relative_to: last.x!.id}}).then(setPosition)
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
