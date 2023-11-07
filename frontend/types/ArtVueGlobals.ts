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
  $makePatcher: (config: PatcherConfig) => Patch,
  // List module funcs
  $getList: (name: string, schema?: ListModuleOpts, uid?: string) => ListController<any>,
  $listenForList: (name: string, uid?: string) => void,
  // Form module funcs
  $getForm: (name: string, formSchema?: NamelessFormSchema, uid?: string) => FormController,
  $listenForForm: (name: string, uid?: string) => void,
  // Character module funcs
  $getCharacter: (name: string, schema?: CharacterModuleOpts, uid?: string) => CharacterController,
  // Profile module funcs
  $getProfile: (name: string, schema?: ProfileModuleOpts, uid?: string) => ProfileController,
  $listenForProfile: (name: string, uid?: string) => void,
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
