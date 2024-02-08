import LineItem from '@/types/LineItem.ts'

export interface RawLineItemSetMap {
  name: string,
  lineItems: LineItem[],
  offer: boolean,
}
