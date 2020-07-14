import Vue from 'vue'
import Component from 'vue-class-component'
import {Mutation} from 'vuex-class'
import {Alert, AlertCategory} from '@/store/state'
import {AxiosError} from 'axios'
import {deriveErrors} from '@/store/forms/helpers'

@Component
export default class Alerts extends Vue {
  @Mutation('pushAlert') public pushAlert: any

  public $alert(alert: Partial<Alert>) {
    (this as any).$store.commit('pushAlert', alert)
  }

  // noinspection JSUnusedGlobalSymbols
  public $errAlert(
    message?: string, timeout?: number,
  ): (error: AxiosError) => void {
    return (error, ignore?: boolean) => {
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
