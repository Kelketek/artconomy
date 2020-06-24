import {VIEWER_TYPE} from '@/types/VIEWER_TYPE'
import {Character} from '@/store/characters/types/Character'

export default interface DeliverableViewSettings {
  viewerType: VIEWER_TYPE,
  showPayment: boolean,
  showAddSubmission: boolean,
  showAddDeliverable: boolean,
  characterInitItems: Character[],
}
