import LineItem from '@/types/LineItem.ts'
import {ListController} from '@/store/lists/controller.ts'

export interface LineItemSetMap {
  name: string,
  lineItems: ListController<LineItem>,
  offer: boolean,
}
