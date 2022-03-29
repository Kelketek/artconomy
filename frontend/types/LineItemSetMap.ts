import LineItem from '@/types/LineItem'
import {ListController} from '@/store/lists/controller'

export interface LineItemSetMap {
  name: string,
  lineItems: ListController<LineItem>
}
