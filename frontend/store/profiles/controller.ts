import Vue from 'vue'
import {Watch} from 'vue-property-decorator'
import Component from 'vue-class-component'
import {ProfileModule} from './index'
import {ProfileModuleOpts} from './types/ProfileModuleOpts'
import {User} from '@/store/profiles/types/User'
import {guestName, setCookie} from '@/lib'
import {SingleController} from '@/store/singles/controller'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {AnonUser} from '@/store/profiles/types/AnonUser'
import {ProfileState} from '@/store/profiles/types/ProfileState'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import {
  artistProfileEndpointFor,
  artistProfilePathFor,
  endpointFor,
  pathFor,
  userPathFor,
} from '@/store/profiles/helpers'
import {BaseController} from '@/store/controller-base'
import {profileRegistry} from '@/store/profiles/registry'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'

@Component
export class ProfileController extends BaseController<ProfileModuleOpts, ProfileState> {
  public baseClass = ProfileModule
  public submoduleKeys = ['user', 'artistProfile']
  public baseModuleName = 'userModules'
  // eslint-disable-next-line camelcase
  public profile_controller__ = true
  public user: SingleController<User|TerseUser|AnonUser> = null as unknown as SingleController<User|TerseUser|AnonUser>
  public artistProfile: SingleController<ArtistProfile> = null as unknown as SingleController<ArtistProfile>
  public products: ListController<Product> = null as unknown as ListController<Product>
  // @ts-ignore
  public registry = profileRegistry

  public updateRoute(newUsername: string, oldUsername: string|undefined) {
    if (newUsername === '_') {
      return
    }
    if (!oldUsername) {
      return
    }
    // Most relevant routes will have the username right in them, so we need to change these.
    const route = {
      name: this.$route.name,
      params: {...this.$route.params},
      query: {...this.$route.query},
      hash: this.$route.hash,
    }
    if ('username' in route.params && (oldUsername === route.params.username)) {
      route.params.username = newUsername
      this.$router.replace(route)
    }
  }

  public kill() {
    // no-op for compatibility.
  }

  public refresh() {
    // Refreshes all subordinate handlers.
    return this.user.refresh().then(() => {
      const user = this.user.x as User
      this.user.endpoint = endpointFor(user.username)
      this.artistProfile.endpoint = artistProfileEndpointFor(user.username)
      if (user.username === '_' || guestName(user.username)) {
        this.artistProfile.setX(null)
      } else {
        return this.$nextTick(() => {
          return this.artistProfile.refresh()
        })
      }
    })
  }

  public get displayName() {
    if (!this.user.x) {
      return ''
    }
    if (this.user.x.username === '_') {
      return ''
    }
    const user = this.user.x as User
    if (user.guest) {
      return `Guest #${user.id}`
    }
    return user.username
  }

  public created() {
    this.register()
    Vue.set(this, 'user', this.$getSingle(
      userPathFor(this.name).join('/'), {endpoint: endpointFor(this.name)}
    ))
    Vue.set(this, 'artistProfile', this.$getSingle(
      artistProfilePathFor(this.name).join('/'), {
        endpoint: artistProfileEndpointFor(this.name), params: {view: 'true'},
      }
    ))
  }

  @Watch('user.x.username')
  public updateUsername(newUsername: string, oldUsername: string|undefined) {
    if (this.name === newUsername) {
      // Initial load. Ignore.
      return
    }
    if (!newUsername) {
      // Destroying instance. No need to make changes.
      return
    }
    this.migrate(newUsername)
    if (this.viewer) {
      this.$store.commit('profiles/setViewerUsername', newUsername)
    }
    this.user.endpoint = endpointFor(newUsername)
    this.artistProfile.endpoint = artistProfileEndpointFor(newUsername)
    this.updateRoute(newUsername, oldUsername)
  }

  @Watch('user.x.csrftoken')
  public updateAuth(newVal: string|undefined) {
    if (!newVal) {
      return
    }
    setCookie('csrftoken', newVal)
    const user = this.user.x as User
    setCookie('authtoken', user.authtoken)
  }

  public attr(name: keyof ProfileState) {
    return this.state[name]
  }

  public get viewer() {
    return this.attr('viewer')
  }

  public get path() {
    return pathFor(this.name)
  }

  public get prefix() {
    return this.path.join('/') + '/'
  }

  public get purged() {
    return !this.state
  }
}
