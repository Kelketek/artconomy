import {Component, mixins} from 'vue-facing-decorator'
import {differenceInYears} from 'date-fns'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {userHandle} from '@/store/profiles/handles.ts'
import {Ratings} from '@/store/profiles/types/Ratings.ts'
import ErrorHandling from '@/mixins/ErrorHandling.ts'
import {useStore} from 'vuex'
import {useProfile} from '@/store/profiles/hooks.ts'
import {ArtState} from '@/store/artState.ts'
import {ArtStore} from '@/store/index.ts'
import {computed} from 'vue'
import {SingleController} from '@/store/singles/controller.ts'
import {parseISO} from '@/lib/otherFormatters.ts'

export interface AgeCheckArgs {
  value: number,
  force?: boolean,
}


const checkStaff = (isLoggedIn: boolean, viewer: User|AnonUser|null) => {
  if (!isLoggedIn) {
    return false
  }
  return Boolean((viewer as User).is_staff)
}

const checkSuperuser = (isLoggedIn: boolean, viewer: User|AnonUser|null) => {
  if (!isLoggedIn) {
    return false
  }
  return Boolean((viewer as User).is_superuser)
}

const loginCheck = (viewer: null|AnonUser|User) => {
  if (!viewer) {
    return false
  }
  return Boolean(viewer.username !== '_')
}

const checkRegistered = (isLoggedIn: boolean, viewer: User|AnonUser|null) => isLoggedIn && !(viewer as User).guest

const getTheocraticBan = () => window.THEOCRATIC_BAN

const getRating = (viewer: User|AnonUser|null) => {
  if (!viewer || viewer.sfw_mode || (getTheocraticBan() && !viewer.verified_adult)) {
    return Ratings.GENERAL
  }
  return viewer.rating
}

const getRawRating = (viewer: User|AnonUser|null) => {
  // The default 'rating' computed property falls back to 0, which means that we ALWAYS change from 0 if we're logged
  // in and not currently using SFW settings. So, if we want to watch for this value's change, but we want to ignore
  // the default rating setting, we use this property instead.
  if (!viewer) {
    return undefined
  }
  if (viewer.sfw_mode) {
    return Ratings.GENERAL
  }
  return viewer.rating
}


const ageCheck = (store: ArtStore, viewer: AnonUser|User, {value, force}: AgeCheckArgs) => {
  if (!value) {
    return
  }
  if (!force) {
    if (viewer.birthday) {
      return
    }
    if (store.state.ageAsked) {
      return
    }
  }
  store.commit('setContentRating', value)
  store.commit('setShowAgeVerification', true)
  store.commit('setAgeAsked', true)
}

const isAdultAllowed = (viewerHandler: ProfileController, theocraticBan: boolean) => {
  if (viewerHandler.user.patchers.sfw_mode.model) {
    return false
  }
  if (theocraticBan && !(viewerHandler.user as SingleController<User|AnonUser>).patchers.verified_adult.model) {
    return false
  }
  const birthday = (viewerHandler.user as SingleController<AnonUser>).patchers.birthday.model
  if (birthday === null) {
    return false
  }
  return differenceInYears(new Date(), parseISO(birthday)) >= 18
}

const hasLandscape = (viewer: User|AnonUser|null) => {
  if (!viewer) {
    return false
  }
  if (!('landscape' in viewer)) {
    return false
  }
  return viewer.landscape
}


export const useViewer = () => {
  const store = useStore<ArtState>()
  const viewerHandler = useProfile(
    store.state.profiles!.viewerRawUsername,
    {persistent: true, viewer: true},
  )
  const viewerName = computed(() => viewerHandler.displayName)
  const rawViewerName = computed(() => store.state.profiles!.viewerRawUsername)
  const viewer = computed(() => viewerHandler.user.x as User|AnonUser)
  const theocraticBan = computed(getTheocraticBan)
  const adultAllowed = computed(() => isAdultAllowed(viewerHandler, theocraticBan.value))
  const isLoggedIn = computed(() => loginCheck(viewer.value))
  const isRegistered = computed(() => checkRegistered(isLoggedIn.value, viewer.value))
  const isStaff = computed(() => checkStaff(isLoggedIn.value, viewer.value))
  const isSuperuser = computed(() => checkSuperuser(isLoggedIn.value, viewer.value))
  const rating = computed(() => getRating(viewer.value))
  const rawRating = computed(() => getRawRating(viewer.value))
  const unverifiedInTheocracy = computed(() => theocraticBan.value && !viewer.value.verified_adult)

  return {
    viewer,
    viewerName,
    rawViewerName,
    viewerHandler,
    adultAllowed,
    isLoggedIn,
    isRegistered,
    isStaff,
    isSuperuser,
    rating,
    rawRating,
    theocraticBan,
    unverifiedInTheocracy,
    ageCheck: (args: AgeCheckArgs) => ageCheck(store, viewer.value, args),
  }
}

// Deprecated.
@Component
export default class Viewer extends mixins(ErrorHandling) {
  public viewerHandler: ProfileController = null as unknown as ProfileController
  @userHandle('viewerHandler')
  public viewer!: User|AnonUser|null

  public get rating(): Ratings {
    return getRating(this.viewer)
  }

  public get rawRating() {
    return getRawRating(this.viewer)
  }

  public get isLoggedIn(): boolean {
    return loginCheck(this.viewer)
  }

  public get isSuperuser(): boolean {
    return checkSuperuser(this.isLoggedIn, this.viewer)
  }

  public get isRegistered(): boolean {
    return checkRegistered(this.isLoggedIn, this.viewer)
  }

  public get isStaff(): boolean {
    return checkStaff(this.isLoggedIn, this.viewer)
  }

  public get landscape() {
    return hasLandscape(this.viewer)
  }

  public get viewerName() {
    return this.viewerHandler.displayName
  }

  public get rawViewerName() {
    return this.$store.state.profiles!.viewerRawUsername
  }

  public get adultAllowed() {
    return isAdultAllowed(this.viewerHandler, this.theocraticBan)
  }

  public get theocraticBan() {
    return window.THEOCRATIC_BAN
  }

  public ageCheck({value, force}: {value: number, force?: boolean}) {
    ageCheck(this.$store, this.viewer!,{value, force})
  }

  public created() {
    this.viewerHandler = this.$getProfile(
      this.rawViewerName, {persistent: true, viewer: true},
    )
  }
}
