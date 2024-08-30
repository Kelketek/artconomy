import {ViewerTypeValue} from '@/types/ViewerType.ts'
import {Character} from '@/store/characters/types/Character.ts'

export default interface DeliverableViewSettings {
  viewerType: ViewerTypeValue,
  showPayment: boolean,
  showAddSubmission: boolean,
  showAddDeliverable: boolean,
  characterInitItems: Character[],
}
