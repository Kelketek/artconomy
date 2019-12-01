// This module should no longer be needed since we're now using the UserHandler plugin.
import Vue from 'vue'
import Component from 'vue-class-component'
import {Mutation, namespace} from 'vuex-class'
import {User} from '@/store/profiles/types/User'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import {ProfileController} from '@/store/profiles/controller'
import {userHandle} from '@/store/profiles/handles'
import {Ratings} from '@/store/profiles/types/Ratings'
import {setCookie} from '@/lib'
import {AxiosError} from 'axios'

const profileModule = namespace('profiles')

@Component
export default class Viewer extends Vue {
  public viewerHandler: ProfileController = null as unknown as ProfileController
  @Mutation('setError', {namespace: 'errors'}) public setError: any
  @userHandle('viewerHandler')
  public viewer!: User|AnonUser|null

  public get rating(): Ratings {
    if (!this.viewer || this.viewer.sfw_mode) {
      return Ratings.GENERAL
    }
    return this.viewer.rating
  }
  public get isLoggedIn(): boolean {
    if (!this.viewer) {
      return false
    }
    return Boolean(this.viewer.username !== '_')
  }
  public get isSuperuser(): boolean {
    if (!this.isLoggedIn) {
      return false
    }
    return Boolean((this.viewer as User).is_superuser)
  }
  public get isRegistered(): boolean {
    return this.isLoggedIn && !(this.viewer as User).guest
  }
  public get isStaff(): boolean {
    if (!this.isLoggedIn) {
      return false
    }
    return Boolean((this.viewer as User).is_staff)
  }
  public get landscape() {
    if (!this.viewer) {
      return false
    }
    if (!('landscape' in this.viewer)) {
      return false
    }
    return this.viewer.landscape
  }
  public get portrait() {
    if (!this.viewer) {
      return false
    }
    if (!('portrait' in this.viewer)) {
      return false
    }
    return this.viewer.portrait
  }
  public get viewerName() {
    return this.viewerHandler.displayName
  }

  public get rawViewerName() {
    return this.$store.state.profiles.viewerRawUsername
  }

  public statusOk(...statuses: number[]) {
    return (error: AxiosError) => {
      if (error.response && statuses.indexOf(error.response.status) !== -1) {
        return
      }
      throw error
    }
  }

  public created() {
    this.viewerHandler = this.$getProfile(
      this.rawViewerName, {persistent: true, viewer: true}
    )
    if (!this.viewerHandler.user.x) {
      this.viewerHandler.user.get().catch(this.setError)
    }
  }
}
