import {Ratings} from '@/types/Ratings.ts'

export interface ShoppingCart {
  product: number,
  email: string,
  private: boolean,
  details: string,
  characters: number[],
  rating: Ratings,
  references: number[],
  named_price: null|number,
  escrow_upgrade: boolean,
}
