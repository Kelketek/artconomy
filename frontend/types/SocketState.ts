import type {ConnectionStatusValue} from '@/types/ConnectionStatus.ts'

export interface SocketState {
  status: ConnectionStatusValue,
  version: string,
  serverVersion: string,
}
