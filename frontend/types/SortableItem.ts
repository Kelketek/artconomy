import {SortableModel} from '@/types/SortableModel.ts'
import {SingleController} from '@/store/singles/controller.ts'

export declare interface SortableItem<T extends SortableModel> {
  id: T[keyof T],
  controller: SingleController<T>
}
