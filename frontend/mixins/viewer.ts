import {Component, mixins} from 'vue-facing-decorator'
import {differenceInYears} from 'date-fns'
import {User} from '@/store/profiles/types/User'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import {ProfileController} from '@/store/profiles/controller'
import {userHandle} from '@/store/profiles/handles'
import {Ratings} from '@/store/profiles/types/Ratings'
import ErrorHandling from '@/mixins/ErrorHandling'
import {parseISO} from '@/lib/lib'

@Component
export default class Viewer extends mixins(ErrorHandling) {
  public viewerHandler: ProfileController = null as unknown as ProfileController
  @userHandle('viewerHandler')
  public viewer!: User|AnonUser|null

  public get rating(): Ratings {
    if (!this.viewer || this.viewer.sfw_mode) {
      return Ratings.GENERAL
    }
    return this.viewer.rating
  }

  public get rawRating() {
    // The default 'rating' computed property falls back to 0, which means that we ALWAYS change from 0 if we're logged
    // in and not currently using SFW settings. So, if we want to watch for this value's change, but we want to ignore
    // the default rating setting, we use this property instead.
    if (!this.viewer) {
      return undefined
    }
    if (this.viewer.sfw_mode) {
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

  public get viewerName() {
    return this.viewerHandler.displayName
  }

  public get rawViewerName() {
    return this.$store.state.profiles!.viewerRawUsername
  }

  public get adultAllowed() {
    if (this.viewerHandler.user.patchers.sfw_mode.model) {
      return false
    }
    // @ts-ignore
    const birthday = this.viewerHandler.user.patchers.birthday.model
    if (birthday === null) {
      return false
    }
    return differenceInYears(new Date(), parseISO(birthday)) >= 18
  }

  public ageCheck({value, force}: {value: number, force?: boolean}) {
    if (!value) {
      return
    }
    if (!force) {
      if (this.viewer!.birthday) {
        return
      }
      if (this.$store.state.ageAsked) {
        return
      }
    }
    this.$store.commit('setContentRating', value)
    this.$store.commit('setShowAgeVerification', true)
    this.$store.commit('setAgeAsked', true)
  }

  public created() {
    this.viewerHandler = this.$getProfile(
      this.rawViewerName, {persistent: true, viewer: true},
    )
  }
}
