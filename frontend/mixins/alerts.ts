import {Component} from 'vue-facing-decorator'
import {Alert, AlertCategory, ArtState} from '@/store/artState.ts'
import {deriveErrors} from '@/store/forms/helpers.ts'
import {ArtVue} from '@/lib/lib.ts'
import {AcServerError} from '@/types/AcServerError.ts'
import {useStore} from 'vuex'

@Component
export default class BaseAlerts extends ArtVue {
  public $alert(alert: Partial<Alert>) {
    (this as any).$store.commit('pushAlert', alert)
  }
}

export const useAlerts = () => {
  const store = useStore<ArtState>()
  const sendAlert = (alert: Partial<Alert> & {message: Alert['message']}) => {
    store.commit('pushAlert', {timeout: 5000, category: AlertCategory.INFO, ...alert})
  }
  return {sendAlert}
}
