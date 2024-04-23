import {ContentRating} from '@/types/ContentRating.ts'

export interface ShoppingCart {
  product: number,
  email: string,
  private: boolean,
  details: string,
  characters: number[],
  rating: ContentRating,
  references: number[],
  named_price: null|number,
  escrow_upgrade: boolean,
}
