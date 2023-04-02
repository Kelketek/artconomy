import Component, {mixins} from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import {userHandle} from '@/store/profiles/handles'
// Used to augment Vue type.
// noinspection ES6UnusedImports
import {Route} from 'vue-router'
import {User} from '@/store/profiles/types/User'
import Viewer from './viewer'
import {ProfileController} from '@/store/profiles/controller'
import {profileRegistry} from '@/store/profiles/registry'

@Component
export default class Subjective extends mixins(Viewer) {
  @Prop({required: true})
  public username!: string

  public protectedView: boolean = false
  public privateView: boolean = false
  public missingOk: boolean = false

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
