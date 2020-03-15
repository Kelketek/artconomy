export default interface Proxy<T> {
  get(): T;
  set(value: T): void;
}
