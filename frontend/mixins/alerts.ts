import {Component} from 'vue-facing-decorator'
import {Alert, AlertCategory} from '@/store/state.ts'
import {deriveErrors} from '@/store/forms/helpers.ts'
import {ArtVue} from '@/lib/lib.ts'
import {AcServerError} from '@/types/AcServerError.ts'

@Component
export default class BaseAlerts extends ArtVue {
  public $alert(alert: Partial<Alert>) {
    (this as any).$store.commit('pushAlert', alert)
  }

  // noinspection JSUnusedGlobalSymbols
  public $errAlert(
    message?: string, timeout?: number,
  ): (error: AcServerError) => void {
    return (error: AcServerError, ignore?: boolean) => {
      const partial: Partial<Alert> = {message: message || deriveErrors(error, []).errors[0]}
      if (timeout !== undefined) {
        partial.timeout = timeout
      }
      const compiled = {...partial, ...{category: AlertCategory.ERROR}};
      // noinspection TypeScriptValidateJSTypes
      (this as any).$alert(compiled)
      if (!ignore) {
        console.trace(error)
      }
    }
  }
}
