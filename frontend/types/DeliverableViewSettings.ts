import {VIEWER_TYPE} from '@/types/VIEWER_TYPE.ts'
import {Character} from '@/store/characters/types/Character.ts'

export default interface DeliverableViewSettings {
  viewerType: VIEWER_TYPE,
  showPayment: boolean,
  showAddSubmission: boolean,
  showAddDeliverable: boolean,
  characterInitItems: Character[],
}
