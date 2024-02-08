import LineItem from '@/types/LineItem'

export interface RawLineItemSetMap {
  name: string,
  lineItems: LineItem[],
  offer: boolean,
}
