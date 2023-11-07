import {ProfileModule} from './index'
import {ProfileModuleOpts} from './types/ProfileModuleOpts'
import {User} from '@/store/profiles/types/User'
import {ComputedGetters, guestName} from '@/lib/lib'
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
import {BaseController, ControllerArgs} from '@/store/controller-base'
import {ListController} from '@/store/lists/controller'
import Product from '@/types/Product'
import {toValue, watch} from 'vue'

@ComputedGetters
export class ProfileController extends BaseController<ProfileModuleOpts, ProfileState> {
  public baseClass = ProfileModule
  public submoduleKeys = ['user', 'artistProfile']
  public baseModuleName = 'userModules'
  public typeName = 'Profile'
  // eslint-disable-next-line camelcase
  public profile_controller__ = true
  public isFetchableController = false
  public user: SingleController<User|TerseUser|AnonUser> = null as unknown as SingleController<User|TerseUser|AnonUser>
  public artistProfile: SingleController<ArtistProfile> = null as unknown as SingleController<ArtistProfile>
  public products: ListController<Product> = null as unknown as ListController<Product>

  public updateRoute = (newUsername: string, oldUsername: string|undefined) => {
    if (newUsername === '_') {
      return
    }
    if (!oldUsername) {
      return
    }
    // Most relevant routes will have the username right in them, so we need to change these.
    /* istanbul ignore next */
    const currentRoute = toValue(this.$root.$route)
    const name = currentRoute.name || undefined
    const route = {
      name,
      params: {...currentRoute.params},
      query: {...currentRoute.query},
      hash: currentRoute.hash,
    }
    if ('username' in route.params && (oldUsername === route.params.username)) {
      route.params.username = newUsername
      this.$root.$router.replace(route)
    }
  }

  public kill = () => {
    // no-op for compatibility.
  }

  public refresh = () => {
    // Refreshes all subordinate handlers.
    return this.user.refresh().then(() => {
      const user = this.user.x as User
      this.user.endpoint = endpointFor(user.username)
      this.artistProfile.endpoint = artistProfileEndpointFor(user.username)
      if (user.username === '_' || guestName(user.username)) {
        this.artistProfile.setX(null)
      } else {
        return this.$root.$nextTick(() => {
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

  constructor(args: ControllerArgs<ProfileModuleOpts>) {
    super(args)
    this.register()
    this.user = this.$root.$getSingle(
      userPathFor(this.name.value).join('/'),
      {
        endpoint: endpointFor(this.name.value),
        socketSettings: {
          appLabel: 'profiles',
          modelName: 'User',
          keyField: 'id',
          serializer: this.viewer ? 'UserSerializer' : 'UserInfoSerializer',
        },
      },
      this._uid,
    )
    this.artistProfile = this.$root.$getSingle(
      artistProfilePathFor(this.name.value).join('/'), {
        endpoint: artistProfileEndpointFor(this.name.value),
        params: {view: 'true'},
        socketSettings: {
          appLabel: 'profiles',
          modelName: 'ArtistProfile',
          keyField: 'id',
          serializer: 'ArtistProfileSerializer',
        },
      },
      this._uid,
    )
    watch(() => this.user.x?.username || '', this.updateUsername)
  }

  // Watcher for user.x.username
  public updateUsername = (newUsername: string, oldUsername: string|undefined) => {
    if (this.name.value === newUsername) {
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

  public attr = <T extends keyof ProfileState>(name: T) => {
    return this.state![name]
  }

  public get viewer() {
    return this.attr('viewer')
  }

  public get path() {
    return pathFor(toValue(this.name))
  }

  public get prefix() {
    return this.path.join('/') + '/'
  }

  public get purged() {
    return !this.state
  }
}
