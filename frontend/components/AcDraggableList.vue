<template>
  <ac-paginated :list="list" :track-pages="trackPages" :ok-statuses="okStatuses" :show-pagination="showPagination">
    <ac-draggable-navs :list="list" :sortable-list="sortableList" position-field="display_position"/>
    <v-col cols="12">
      <draggable
          tag="v-row"
          :component-data="{'no-gutters': true}"
          v-model="sortableList"
          :group="{name: 'main', put: false, pull: 'clone'}"
          :force-fallback="true"
      >
        <slot :sortableList="sortableList"/>
      </draggable>
    </v-col>
    <ac-draggable-navs :list="list" :sortable-list="sortableList" position-field="display_position" class="pt-5"/>
    <template v-slot:failure>
      <v-col class="text-center" v-if="okStatuses"><p>{{failureMessage}}</p></v-col>
    </template>
    <template v-slot:empty>
      <v-col class="text-center" v-if="emptyMessage"><p>{{emptyMessage}}</p></v-col>
    </template>
  </ac-paginated>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import draggable from 'vuedraggable'
import AcDraggableNavs from '@/components/AcDraggableNavs.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import diff, {DiffPatch} from 'list-diff.js'
import Submission from '@/types/Submission'
import {artCall} from '@/lib/lib'

@Component({
  components: {
    AcPaginated,
    AcDraggableNavs,
    draggable,
  },
})
class AcDraggableList extends Vue {
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

  @Prop({required: true})
  public list!: ListController<any>

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
      artCall({
        url: `${target.endpoint}up/`,
        method: 'post',
        data: {relative_to: first.x!.id},
      }).then(setPosition)
      return
    }
    if (index === (newVersion.length - 1)) {
      const last = this.sortableList[index]
      target.updateX({display_position: last.patchers.display_position.model - 0.1})
      artCall({
        url: `${target.endpoint}down/`,
        method: 'post',
        data: {relative_to: last.x!.id},
      }).then(setPosition)
      return
    }
    // Averaging what's in front and behind will set this item's position between.
    target.patchers.display_position.model = (
        newVersion[index - 1].patchers.display_position.model +
        newVersion[index + 1].patchers.display_position.model
    ) / 2
  }
}

export default toNative(AcDraggableList)
</script>
