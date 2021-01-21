import {ConnectionStatus} from '@/types/ConnectionStatus'

export interface SocketState {
  status: ConnectionStatus,
  version: string,
  serverVersion: string,
}
