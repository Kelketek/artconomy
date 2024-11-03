
import {useViewer} from './viewer.ts'
import {usePricing} from '@/mixins/PricingAware.ts'
import {useProfile} from '@/store/profiles/hooks.ts'
import {computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'
import type {ServicePlan, SubjectiveProps} from '@/types/main'
import {StaffPower, TerseUser, User} from '@/store/profiles/types/main'

const getIsCurrent = (username: string, rawViewerName: string, viewerName: string) => {
  return username === rawViewerName || username === viewerName
}

const getSubjectPlan = (subject: TerseUser | User | null, getPlan: (planName: string) => ServicePlan | null) => {
  subject = subject as User
  if (!subject || !subject.service_plan) {
    return null
  }
  return getPlan(subject.service_plan)
}

export const useSubject = <T extends SubjectiveProps>({ props, privateView = false, controlPowers = [] }: { props: T; privateView?: boolean; protectedView?: boolean, controlPowers?: StaffPower[] }) => {
  const {
    viewerName,
    rawViewerName,
    isSuperuser,
    isRegistered,
    powers,
  } = useViewer()
  const subjectHandler = useProfile(props.username)

  const subject = computed(() => subjectHandler.user.x as TerseUser | User)
  const isCurrent = computed(() => getIsCurrent(props.username, rawViewerName.value, viewerName.value))
  const controls = computed(() => {
    if (isCurrent.value) {
      return true
    }
    if (controlPowers.length === 0) {
      return isSuperuser.value
    }
    for (const entry of controlPowers) {
      if (powers.value[entry]) {
        return true
      }
    }
    return false
  })
  const {getPlan} = usePricing()
  const subjectPlan = computed(() => getSubjectPlan(subject.value, getPlan))
  const store = useStore()
  // Putting the calls for useRoute and useRouter behind these conditionals so that we don't need the
  // router for as many tests.
  if (privateView && !isRegistered.value) {
    useRouter().replace({
      name: 'Login',
      query: {next: useRoute().fullPath},
    }).then()
  } else if (privateView && !controls.value) {
    store.commit('errors/setError', {response: {status: 403}})
  }
  const promise = subjectHandler.user.get()
  return {
    promise,
    subject,
    subjectHandler,
    isCurrent,
    controls,
    subjectPlan,
  }
}
