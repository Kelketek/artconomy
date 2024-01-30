import {ArtStore} from '@/store'
import {SocketManager} from '@/plugins/socket'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts'
import {SingleController} from '@/store/singles/controller'
import {Patch, PatcherConfig} from '@/store/singles/patcher'
import {ListModuleOpts} from '@/store/lists/types/ListModuleOpts'
import {ListController} from '@/store/lists/controller'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema'
import {FormController} from '@/store/forms/form-controller'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'
import {CharacterController} from '@/store/characters/controller'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts'
import {ProfileController} from '@/store/profiles/controller'
import {RouteLocation, Router} from 'vue-router'
import {createVuetify} from 'vuetify'
import {ArtVueInterface} from '@/types/ArtVueInterface'
import {SingleRegistry} from '@/store/singles/registry'
import {ListRegistry} from '@/store/lists/registry'
import {CharacterRegistry} from '@/store/characters/registry'
import {ProfileRegistry} from '@/store/profiles/registry'
import {FormRegistry} from '@/store/forms/registry'
import {RegistryRegistry} from '@/store/registry-base'

export interface ArtVueGlobals {
  _uid: string,
  // Store
  $store: ArtStore,
  // Socket
  $sock: SocketManager,
  // Shortcuts
  $displayImage: (asset: object, thumbName: string) => string,
  $img: (asset: object | null, thumbName: string, fallback?: boolean) => string,
  $goTo: (selector: string) => void,
  // Single module funcs
  $getSingle: (name: string, schema?: SingleModuleOpts<any>, uid?: string) => SingleController<any>,
  $listenForSingle: (name: string, uid?: string) => void,
  $registryForSingle: () => SingleRegistry,
  // List module funcs
  $getList: (name: string, schema?: ListModuleOpts, uid?: string) => ListController<any>,
  $listenForList: (name: string, uid?: string) => void,
  $registryForList: () => ListRegistry,
  // Form module funcs
  $getForm: (name: string, formSchema?: NamelessFormSchema, uid?: string) => FormController,
  $listenForForm: (name: string, uid?: string) => void,
  $registryForForm: () => FormRegistry,
  // Character module funcs
  $getCharacter: (name: string, schema?: CharacterModuleOpts, uid?: string) => CharacterController,
  $listenForCharacter: (name: string, uid?: string) => void,
  $registryForCharacter: () => CharacterRegistry,
  // Profile module funcs
  $getProfile: (name: string, schema?: ProfileModuleOpts, uid?: string) => ProfileController,
  $listenForProfile: (name: string, uid?: string) => void,
  $registryForProfile: () => ProfileRegistry,
  $registries: RegistryRegistry,
  // Vue Router
  $router: Router,
  $route: RouteLocation,
  // Vuetify
  $vuetify: ReturnType<typeof createVuetify>
  $nextTick: (callBack?: () => void) => Promise<void>,
  $root: ArtVueInterface,
  $menuTarget: string|false,
  $statusTarget: string|false,
  $snackbarTarget: string|false,
  $modalTarget: string|false,
}
