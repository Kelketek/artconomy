import Proxy from '@/store/singles/types/Proxy'

export type Proxify<T> = {
  [P in keyof T]: Proxy<T[P]>;
}
