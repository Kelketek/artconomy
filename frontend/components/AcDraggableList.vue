<template>
  <ac-paginated
    :list="list"
    :track-pages="trackPages"
    :ok-statuses="okStatuses"
    :show-pagination="showPagination"
  >
    <ac-draggable-navs
      :list="list"
      :sortable-list="sortableList"
      position-field="display_position"
    />
    <v-col cols="12">
      <Sortable
        tag="div"
        :options="{group: {name: 'main', put: false, pull: 'clone'}, store}"
        class="v-row"
        :list="sortableList"
        item-key="id"
        @update="moveItemInList"
      >
        <template #item="{element, index}">
          <slot
            :element="element.controller"
            :index="index"
          />
        </template>
      </Sortable>
    </v-col>
    <ac-draggable-navs
      :list="list"
      :sortable-list="sortableList"
      class="pt-5"
    />
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

<script setup lang="ts" generic="T extends SortableModel">
import {Sortable} from 'sortablejs-vue3'
import AcDraggableNavs from '@/components/AcDraggableNavs.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import diff, {DELETION, DiffPatch, INSERTION} from 'list-diff.js'
import {artCall} from '@/lib/lib.ts'
import {VCol} from 'vuetify/lib/components/VGrid/index.mjs'
import {SortableEvent} from 'sortablejs'
import {computed} from 'vue'
import {SingleController} from '@/store/singles/controller.ts'

import type {AcDraggableListProps, SortableItem, SortableModel} from '@/types/main'

const props = withDefaults(defineProps<AcDraggableListProps<T>>(), {
  trackPages: false,
  okStatuses: () => [],
  failureMessage: '',
  emptyMessage: '',
  showPagination: true,
})

const listToSortable = (list: SingleController<T>[]): SortableItem<T>[] => {
  return list.map((controller) => ({id: controller.x![props.list.keyProp], controller: controller}))
}

const sortableList = computed({
  get(): SortableItem<T>[] {
    const list = listToSortable(props.list.list)
    // Mark this for forced reactivity. The sorting does not seem to be reacting deeply to the model values as expected.
    list.sort((a, b) => -(a.controller.patchers.display_position.model - b.controller.patchers.display_position.model))
    return list
  },
  set(newVersion) {
    // This function should only be used by Sortable. It is not a general purpose way to modify the list.
    // Doing anything else with it is liable to break things.
    //
    // Need to find the difference here.
    const keyProp = props.list.keyProp
    const a = sortableList.value.map((item) => item.id)
    const b = newVersion.map((item) => item.id)
    const moves = diff(a, b)
    // Nothing has changed.
    if (moves.length === 0) {
      return
    }
    let index: number
    let move: DiffPatch<T[keyof T]>
    const oldList = [...sortableList.value]
    if (moves.length === 1 && moves[0].type === DELETION) {
      move = moves[0]
      oldList[move.index].controller.deleted = true
      return
    }
    // This is the insertion move. It tells us the target index where our resulting item was inserted.
    move = moves.filter((move) => move.type === INSERTION)[0]
    index = move.index
    // If we delete after the fact, it means that our target index will shift downward. The algorithm only deletes
    // afterward in cases where our index will shift down-- it doesn't do it when moving us toward the beginning,
    // but to the end.
    if (moves[1].type === DELETION) {
      index -= 1
    }
    const setPosition = (response: T) => {
      target.setX(response)
      target.patchers.display_position.model = response.display_position
    }
    const target = newVersion[index].controller
    if (index === 0) {
      // There must be one other entry or else the drag-and-drop would create no difference.
      //
      // However, we really need to know the on-server 'up' value on this one to do this right.
      const first = oldList[index].controller
      target.updateX({display_position: first.patchers.display_position.model + 0.1} as Partial<T>)
      artCall({
        url: `${target.endpoint}up/`,
        method: 'post',
        data: {relative_to: first.x![keyProp]},
      }).then(setPosition)
      return
    }
    if (index === (newVersion.length - 1)) {
      const last = oldList[index].controller
      // Ditto here.
      // @ts-expect-error TypeScript being obtuse.
      target.updateX({display_position: last.patchers.display_position.model - 0.1})
      artCall({
        url: `${target.endpoint}down/`,
        method: 'post',
        data: {relative_to: last.x![keyProp]},
      }).then(setPosition)
      return
    }
    // Averaging what's in front and behind will set this item's position between.
    target.patchers.display_position.model = (
        newVersion[index - 1].controller.patchers.display_position.model +
        newVersion[index + 1].controller.patchers.display_position.model
    ) / 2
  },
})

const store = {
  get: () => [...sortableList.value],
  set: () => {},
}

const moveItemInList = (event: SortableEvent) => {
  const array = [...sortableList.value]
  const from = event.oldIndex
  const to = event.newIndex
  if (!(typeof from === 'number' && typeof to === 'number')) {
    // Bogus instructions. Ignore.
    return
  }
  const item = array.splice(from, 1)[0]
  array.splice(to, 0, item)
  sortableList.value = array
}
</script>
