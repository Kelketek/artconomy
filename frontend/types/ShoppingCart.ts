import type {RatingsValue} from '@/types/Ratings.ts'

export interface ShoppingCart {
  product: number,
  email: string,
  private: boolean,
  details: string,
  characters: number[],
  rating: RatingsValue,
  references: number[],
  named_price: null|number,
  escrow_upgrade: boolean,
}
