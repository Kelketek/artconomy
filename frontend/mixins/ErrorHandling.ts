// This module should no longer be needed since we're now using the UserHandler plugin.
import {Component} from 'vue-facing-decorator'
import {AxiosError} from 'axios'
import {ArtVue} from '@/lib/lib.ts'
import {useStore} from 'vuex'

@Component
export default class ErrorHandling extends ArtVue {
  public statusOk(...statuses: number[]) {
    return statusOk(...statuses)
  }

  public setError(error: Error) {
    this.$store.commit('errors/setError', error)
  }
}

export const statusOk = (...statuses: number[]) => {
  return (error: AxiosError) => {
    if (error.response && statuses.indexOf(error.response.status) !== -1) {
      return
    }
    throw error
  }
}

export const setError = (error: Error) => {
  const store = useStore()
  store.commit('errors/setError', error)
}
