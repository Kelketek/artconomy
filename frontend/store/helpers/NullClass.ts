export class NullClass {
  constructor(...args: any[]) {
    throw Error('Class not specified.')
  }
}
