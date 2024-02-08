<template>
  <v-col cols="12">
    <v-row no-gutters>
      <Sortable
          tag="div"
          :list="previousList"
          :group="{name: 'previous', put: () => true, pull: false}"
          class="page-setter v-col v-col-6"
          @add="addPrevious"
          :item-key="list.keyProp"
      >
        <template #item><div v-show="false"></div></template>
        <template v-slot:header>
          <v-card :class="{disabled: list.currentPage === 1}" v-show="list.totalPages !== 1">
            <v-card-text class="text-center">
              Previous
            </v-card-text>
          </v-card>
        </template>
      </Sortable>
      <Sortable
          tag="div"
          :component-data="{cols: 6}"
          :list="nextList"
          :group="{name: 'next', put: () => true, pull: false}"
          class="page-setter v-col"
          @add="addNext"
          :item-key="list.keyProp"
      >
        <template #item><div v-show="false"></div></template>
        <template v-slot:header>
          <v-card :class="{disabled: list.currentPage === list.totalPages}" v-show="list.totalPages !== 1">
            <v-card-text class="text-center">
              Next
            </v-card-text>
          </v-card>
        </template>
      </Sortable>
    </v-row>
    <v-col cols="12" class="py-2"> </v-col>
  </v-col>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import { Sortable } from "sortablejs-vue3"
import {artCall} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller'
import {ListController} from '@/store/lists/controller'

@Component({
  components: {
    Sortable,
  },
})
class AcDraggableNavs<T extends object> extends Vue {
  @Prop({required: true})
  public sortableList!: SingleController<T>[]

  @Prop({required: true})
  public list!: ListController<T>

  @Prop({required: true})
  public positionField!: string & keyof T

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
    artCall({
      url: `${controller.endpoint}${suffix}/`,
      method: 'post',
      data: {current_value: borderController.x![this.positionField]},
    }).catch(() => {
      if (controller.purged) {
        return
      }
      controller.deleted = false
    })
    controller.deleted = true
  }
}

export default toNative(AcDraggableNavs)
</script>
