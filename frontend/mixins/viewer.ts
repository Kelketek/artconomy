import {differenceInYears} from 'date-fns'
import {User} from '@/store/profiles/types/User.ts'
import {AnonUser} from '@/store/profiles/types/AnonUser.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import type {RatingsValue} from '@/types/Ratings.ts'
import {useStore} from 'vuex'
import {useProfile} from '@/store/profiles/hooks.ts'
import {ArtState} from '@/store/artState.ts'
import {ArtStore} from '@/store/index.ts'
import {computed, watch} from 'vue'
import {SingleController} from '@/store/singles/controller.ts'
import {parseISO} from '@/lib/otherFormatters.ts'
import {Ratings} from '@/types/Ratings.ts'
import {StaffPower} from '@/store/profiles/types/StaffPowers.ts'

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

const getRawRating = (viewer: User|AnonUser|null): RatingsValue|undefined => {
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
  if (window.PRERENDERING) {
    return
  }
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

export const POWER_LIST: StaffPower[] = [
  'handle_disputes', 'view_social_data', 'view_financials', 'moderate_content', 'moderate_discussion',
  'table_seller', 'view_as', 'administrate_users',
] as const

export const buildPowers = (handler: ProfileController) => computed((): Record<StaffPower, boolean> => {
  if (!handler.user.x?.is_staff || !handler.staffPowers.x) {
    return Object.fromEntries(POWER_LIST.map((key) => [key, false])) as Record<StaffPower, boolean>
  }
  if (handler.user.x?.is_superuser) {
    return Object.fromEntries(POWER_LIST.map((key) => [key, true])) as Record<StaffPower, boolean>
  }
  return Object.fromEntries(
    Object.entries(handler.staffPowers.x).filter(([_key, value]) => typeof value === 'boolean')
  ) as Record<StaffPower, boolean>
})


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
  // TODO: Remove once tests are updated.
  const isStaff = computed(() => checkStaff(isLoggedIn.value, viewer.value))
  const isSuperuser = computed(() => checkSuperuser(isLoggedIn.value, viewer.value))
  const rating = computed(() => getRating(viewer.value))
  const rawRating = computed(() => getRawRating(viewer.value))
  const unverifiedInTheocracy = computed(() => theocraticBan.value && !viewer.value.verified_adult)
  const landscape = computed(() => hasLandscape(viewer.value))
  watch(() => viewer.value?.is_staff, (flag) => {
    if (!flag) {
      return
    }
    viewerHandler.staffPowers.get().catch(() => {})
  }, {immediate: true})
  const powers = buildPowers(viewerHandler)

  return {
    viewer,
    viewerName,
    rawViewerName,
    viewerHandler,
    adultAllowed,
    isLoggedIn,
    isRegistered,
    // TODO: Remove once tests are updated.
    isStaff,
    isSuperuser,
    rating,
    rawRating,
    theocraticBan,
    unverifiedInTheocracy,
    landscape,
    powers,
    ageCheck: (args: AgeCheckArgs) => ageCheck(store, viewer.value, args),
  }
}
