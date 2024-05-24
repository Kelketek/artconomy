import {ListController} from '@/store/lists/controller.ts'
import {SortableModel} from '@/types/SortableModel.ts'

export declare interface AcDraggableListProps<T extends SortableModel> {
  trackPages?: boolean,
  okStatuses?: number[],
  failureMessage?: string,
  emptyMessage?: string,
  showPagination?: boolean,
  list: ListController<T>,
}
