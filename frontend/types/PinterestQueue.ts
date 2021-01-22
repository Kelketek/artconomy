import {QueueIntake} from '@/types/QueueIntake'

export declare interface PinterestQueue extends QueueIntake {
  queue: any[],
  version: string,
  tagId?: string,
  newLoad: (tagId: string) => void,
}
