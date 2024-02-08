// This module should no longer be needed since we're now using the UserHandler plugin.
import {Component} from 'vue-facing-decorator'
import {userHandle} from '@/store/profiles/handles.ts'
import {AxiosError} from 'axios'
import {ArtVue} from '@/lib/lib.ts'

@Component
export default class ErrorHandling extends ArtVue {
  // @ts-ignore
  @userHandle('viewerHandler')
  public statusOk(...statuses: number[]) {
    return (error: AxiosError) => {
      if (error.response && statuses.indexOf(error.response.status) !== -1) {
        return
      }
      throw error
    }
  }

  public setError(error: Error) {
    this.$store.commit('errors/setError', error)
  }
}
