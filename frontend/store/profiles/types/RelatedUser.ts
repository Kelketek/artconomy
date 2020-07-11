export interface RelatedUser {
  id: number,
  username: string,
  avatar_url: string,
  stars: number|null,
  rating_count: number,
  is_staff: boolean,
  is_superuser: boolean,
  artist_mode: boolean|null,
  guest: boolean,
  taggable: boolean,
}
