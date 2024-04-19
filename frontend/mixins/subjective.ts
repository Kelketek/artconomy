import {Component, mixins, Prop, Watch} from 'vue-facing-decorator'
import {userHandle} from '@/store/profiles/handles.ts'
// Used to augment Vue type.
// noinspection ES6UnusedImports
import {User} from '@/store/profiles/types/User.ts'
import Viewer, {useViewer} from './viewer.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {profileRegistry} from '@/store/profiles/registry.ts'
import PricingAware, {usePricing} from '@/mixins/PricingAware.ts'
import {useProfile} from '@/store/profiles/hooks.ts'
import {computed} from 'vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {ServicePlan} from '@/types/ServicePlan.ts'
import {useRoute, useRouter} from 'vue-router'
import {useStore} from 'vuex'

@Component
export default class Subjective extends mixins(Viewer, PricingAware) {
  @Prop({required: true})
  public username!: string

  public protectedView: boolean = false
  public privateView: boolean = false
  public missingOk: boolean = false

  // @ts-ignore
  @userHandle('subjectHandler')
  public subject!: User | null

  public subjectHandler: ProfileController = null as unknown as ProfileController

  public get isCurrent(): boolean {
    return getIsCurrent(this.username, this.rawViewerName, this.viewerName)
  }

  public get controls(): boolean {
    return getControls(this.isCurrent, this.protectedView, this.isSuperuser, this.isStaff)
  }

  public get subjectPlan() {
    if (!this.subject || !this.subject.service_plan) {
      return null
    }
    return this.getPlan(this.subject.service_plan)
  }

  @Watch('username')
  public updateUsername() {
    profileRegistry.unhook((this as any)._uid, this.subjectHandler)
    this.rebuildHandler()
  }

  public rebuildHandler() {
    if (this.missingOk && !this.username) {
      return
    }
    this.subjectHandler = this.$getProfile(this.username, {})
    const promise = this.subjectHandler.user.get()
    if (!this.missingOk) {
      promise.catch(this.setError)
    } else {
      promise.catch(() => undefined)
    }
  }

  public created() {
    if (this.privateView && !this.isRegistered) {
      this.$router.replace({
        name: 'Login',
        query: {next: this.$route.fullPath},
      })
    } else if (this.privateView && !this.controls) {
      this.$store.commit('errors/setError', {response: {status: 403}})
    }
    this.rebuildHandler()
  }
}

const getIsCurrent = (username: string, rawViewerName: string, viewerName: string) => {
  return username === rawViewerName || username === viewerName
}

const getControls = (isCurrent: boolean, protectedView: boolean, isSuperuser: boolean, isStaff: boolean) => {
  if (isCurrent) {
    return true
  }
  if (protectedView) {
    return isSuperuser
  }
  return isStaff
}

const getSubjectPlan = (subject: TerseUser | User | null, getPlan: (planName: string) => ServicePlan | null) => {
  subject = subject as User
  if (!subject || !subject.service_plan) {
    return null
  }
  return getPlan(subject.service_plan)
}

export const useSubject = <T extends SubjectiveProps>(props: T, privateView = false, protectedView = false) => {
  const {
    viewerName,
    rawViewerName,
    isSuperuser,
    isStaff,
    isRegistered,
  } = useViewer()
  const subjectHandler = useProfile(props.username)

  const subject = computed(() => subjectHandler.user.x as TerseUser | User)
  const isCurrent = computed(() => getIsCurrent(props.username, rawViewerName.value, viewerName.value))
  const controls = computed(() => getControls(isCurrent.value, protectedView, isSuperuser.value, isStaff.value))
  const {getPlan} = usePricing()
  const subjectPlan = computed(() => getSubjectPlan(subject.value, getPlan))
  const store = useStore()
  // Putting the calls for useRoute and useRouter behind these conditionals so that we don't need the
  // router for as many tests.
  if (privateView && !isRegistered) {
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
