import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'

export default interface DeliverableViewSettings {
  viewerType: VIEWER_TYPE,
  showPayment: boolean,
  showAddSubmission: boolean,
}
