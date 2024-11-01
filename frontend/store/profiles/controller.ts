import {ProfileModule} from './index.ts'
import {ComputedGetters} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {
  artistProfileEndpointFor,
  artistProfilePathFor,
  endpointFor,
  pathFor, staffPowersEndpointFor, staffPowersPathFor,
  userPathFor,
} from '@/store/profiles/helpers.ts'
import {BaseController, ControllerArgs} from '@/store/controller-base.ts'
import {ListController} from '@/store/lists/controller.ts'
import {nextTick, toValue, watch} from 'vue'
import {getController} from '@/store/registry-base.ts'
import {guestName} from '@/lib/otherFormatters.ts'
import type {Product} from '@/types/main'
import type {SingleModuleOpts, SingleState} from '@/store/singles/types.d.ts'
import {
  AnonUser,
  ArtistProfile,
  ProfileModuleOpts,
  ProfileState,
  StaffPowers,
  TerseUser, User,
} from '@/store/profiles/types/main'

export type AnyUser = User | TerseUser | AnonUser

@ComputedGetters
export class ProfileController extends BaseController<ProfileModuleOpts, ProfileState> {
  public baseClass = ProfileModule
  public submoduleKeys = ['user', 'artistProfile', 'staffPowers']
  public baseModuleName = 'userModules'
  public typeName: 'Profile' = 'Profile'
  // eslint-disable-next-line camelcase
  public profile_controller__ = true
  public isFetchableController = false
  public user = null as unknown as SingleController<AnyUser>
  public artistProfile = null as unknown as SingleController<ArtistProfile>
  public staffPowers = null as unknown as SingleController<StaffPowers>
  public products = null as unknown as ListController<Product>

  public updateRoute = (newUsername: string, oldUsername: string | undefined) => {
    if (newUsername === '_') {
      return
    }
    if (!oldUsername) {
      return
    }
    // Most relevant routes will have the username right in them, so we need to change these.
    /* istanbul ignore next */
    const currentRoute = toValue(this.$router.currentRoute)
    const name = currentRoute.name || undefined
    const route = {
      name,
      params: {...currentRoute.params},
      query: {...currentRoute.query},
      hash: currentRoute.hash,
    }
    if ('username' in route.params && (oldUsername === route.params.username)) {
      route.params.username = newUsername
      this.$router.replace(route)
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
        return nextTick(() => {
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
    this.user = getController<SingleState<AnyUser>, SingleModuleOpts<AnyUser>, SingleController<AnyUser>>({
      uid: this._uid,
      name: userPathFor(this.name.value).join('/'),
      typeName: 'Single',
      socket: this.$sock,
      router: this.$router,
      store: this.$store,
      schema: {
        endpoint: endpointFor(this.name.value),
        socketSettings: {
          appLabel: 'profiles',
          modelName: 'User',
          keyField: 'id',
          serializer: this.viewer ? 'UserSerializer' : 'UserInfoSerializer',
        },
      },
      registries: this.$registries,
      ControllerClass: SingleController,
    })
    this.artistProfile = getController<SingleState<ArtistProfile>, SingleModuleOpts<ArtistProfile>, SingleController<ArtistProfile>>({
      uid: this._uid,
      name: artistProfilePathFor(this.name.value).join('/'),
      typeName: 'Single',
      router: this.$router,
      socket: this.$sock,
      store: this.$store,
      schema: {
        endpoint: artistProfileEndpointFor(this.name.value),
        params: {view: 'true'},
        socketSettings: {
          appLabel: 'profiles',
          modelName: 'ArtistProfile',
          keyField: 'id',
          serializer: 'ArtistProfileSerializer',
        },
      },
      registries: this.$registries,
      ControllerClass: SingleController,
    })
    this.staffPowers = getController<SingleState<StaffPowers>, SingleModuleOpts<StaffPowers>, SingleController<StaffPowers>>({
      uid: this._uid,
      name: staffPowersPathFor(this.name.value).join('/'),
      typeName: 'Single',
      router: this.$router,
      socket: this.$sock,
      store: this.$store,
      schema: {
        endpoint: staffPowersEndpointFor(this.name.value),
        socketSettings: {
          appLabel: 'profiles',
          modelName: 'StaffPowers',
          keyField: 'id',
          serializer: 'StaffPowersSerializer',
        }
      },
      registries: this.$registries,
      ControllerClass: SingleController,
    })
    watch(() => this.user.x?.username || '', this.updateUsername)
  }

  // Watcher for user.x.username
  public updateUsername = (newUsername: string, oldUsername: string | undefined) => {
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
    this.staffPowers.endpoint = staffPowersEndpointFor(newUsername)
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
}
