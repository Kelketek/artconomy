import Proxy from '@/store/singles/types/Proxy.ts'

export type Proxify<T> = {
  [P in keyof T]: Proxy<T[P]>;
}
