// This module should no longer be needed since we're now using the UserHandler plugin.
import Vue from 'vue'
import Component from 'vue-class-component'
import {Mutation} from 'vuex-class'
import {userHandle} from '@/store/profiles/handles'
import {AxiosError} from 'axios'

@Component
export default class ErrorHandling extends Vue {
  @Mutation('setError', {namespace: 'errors'}) public setError: any
  @userHandle('viewerHandler')
  public statusOk(...statuses: number[]) {
    return (error: AxiosError) => {
      if (error.response && statuses.indexOf(error.response.status) !== -1) {
        return
      }
      throw error
    }
  }
}
