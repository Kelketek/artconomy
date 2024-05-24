import {SortableModel} from '@/types/SortableModel.ts'
import {SortableItem} from '@/types/SortableItem.ts'
import {ListController} from '@/store/lists/controller.ts'

export declare interface AcDraggableNavsProps<T extends SortableModel> {
  sortableList: SortableItem<T>[],
  list: ListController<T>,
}
