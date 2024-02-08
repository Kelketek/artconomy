<template>
  <v-col cols="12">
    <v-row no-gutters>
      <Sortable
          tag="div"
          :list="previousList"
          :options="{group: {name: 'previous', put: true, pull: false}, disabled: list.currentPage === 1, removeCloneOnHide: false}"
          class="page-setter v-col v-col-6"
          @add="addPrevious"
          item-key="id"
      >
        <template #header>
          <v-card :class="{disabled: list.currentPage === 1}">
            <v-card-text class="text-center">
              Previous
            </v-card-text>
          </v-card>
        </template>
        <template #item="{index}"><span v-show="false" :key="index"/></template>
      </Sortable>
      <Sortable
          tag="div"
          :list="nextList"
          :options="{group: {name: 'next', put: true, pull: false}, disabled: list.currentPage === list.totalPages}"
          class="page-setter v-col"
          @add="addNext"
          item-key="id"
      >
        <template #item="{index}"><span v-show="false" :key="index"/></template>
        <template #header>
          <v-card :class="{disabled: list.currentPage === list.totalPages}">
            <v-card-text class="text-center">
              Next
            </v-card-text>
          </v-card>
        </template>
      </Sortable>
    </v-row>
  </v-col>
</template>

<style>
/*
No idea why, but there seems to be no way to hide the resulting drop aside from this.
Make sure any draggable item has the .draggable-item class or it won't be properly hidden.
*/
.page-setter .draggable-item {
  display: none;
}
</style>

<script setup lang="ts" generic="T extends SortableModel">
import { Sortable } from "sortablejs-vue3"
import {artCall} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import {SortableModel} from '@/types/SortableModel.ts'
import {ref} from 'vue'
import {SortableItem} from '@/types/SortableItem.ts'

declare interface AcDraggableNavsProps {
  sortableList: SortableItem<T>[],
  list: ListController<T>,
}

const props = defineProps<AcDraggableNavsProps>()

const previousList = ref([])
const nextList = ref([])

const adder = (addEvent: any, previous: boolean) => {
  const controller = props.sortableList[addEvent.oldIndex].controller
  let borderIndex: number
  let suffix: string
  if (previous) {
    suffix = 'up'
    borderIndex = 0
  } else {
    suffix = 'down'
    borderIndex = props.sortableList.length - 1
  }
  const borderController = props.sortableList[borderIndex].controller
  artCall({
    url: `${controller.endpoint}${suffix}/`,
    method: 'post',
    data: {current_value: borderController.x!.display_position},
  }).catch(() => {
    if (controller.purged) {
      return
    }
    controller.deleted = false
  })
  controller.deleted = true
}

const addNext = (addEvent: any) => {
  adder(addEvent, false)
}

const addPrevious = (addEvent: any) => {
  if (props.list.currentPage === 1) {
    return
  }
  adder(addEvent, true)
}
</script>
