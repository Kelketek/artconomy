import {ConnectionStatus} from '@/types/ConnectionStatus.ts'

export interface SocketState {
  status: ConnectionStatus,
  version: string,
  serverVersion: string,
}
