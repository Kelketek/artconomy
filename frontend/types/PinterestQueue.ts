import {QueueIntake} from '@/types/QueueIntake.ts'

export declare interface PinterestQueue extends QueueIntake {
  queue: any[],
  version: string,
  tagId?: string,
}
