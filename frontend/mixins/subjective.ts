import {Component, mixins, Prop, Watch} from 'vue-facing-decorator'
import {userHandle} from '@/store/profiles/handles.ts'
// Used to augment Vue type.
// noinspection ES6UnusedImports
import {User} from '@/store/profiles/types/User.ts'
import Viewer from './viewer.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {profileRegistry} from '@/store/profiles/registry.ts'
import PricingAware from '@/mixins/PricingAware.ts'

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
    return this.username === this.rawViewerName || this.username === this.viewerName
  }

  public get controls(): boolean {
    if (this.isCurrent) {
      return true
    }
    if (this.protectedView) {
      return this.isSuperuser
    }
    return this.isStaff
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
      this.$router.replace({name: 'Login', query: {next: this.$route.fullPath}})
    } else if (this.privateView && !this.controls) {
      this.$store.commit('errors/setError', {response: {status: 403}})
    }
    this.rebuildHandler()
  }
}
