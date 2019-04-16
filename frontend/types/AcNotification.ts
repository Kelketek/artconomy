export default interface AcNotification<T, D> {
  event: {
    id: number,
    type: number,
    data: D,
    date: string,
    target: T,
  },
  read: boolean,
  id: number
}
