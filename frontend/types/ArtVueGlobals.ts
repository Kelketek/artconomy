import {ArtStore} from '@/store/index.ts'
import {SocketManager} from '@/plugins/socket.ts'
import {SingleModuleOpts} from '@/store/singles/types/SingleModuleOpts.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ListModuleOpts} from '@/store/lists/types/ListModuleOpts.ts'
import {ListController} from '@/store/lists/controller.ts'
import {NamelessFormSchema} from '@/store/forms/types/NamelessFormSchema.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts.ts'
import {CharacterController} from '@/store/characters/controller.ts'
import {ProfileModuleOpts} from '@/store/profiles/types/ProfileModuleOpts.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {RouteLocation, Router} from 'vue-router'
import {createVuetify} from 'vuetify'
import {ArtVueInterface} from '@/types/ArtVueInterface.ts'
import {SingleRegistry} from '@/store/singles/registry.ts'
import {ListRegistry} from '@/store/lists/registry.ts'
import {CharacterRegistry} from '@/store/characters/registry.ts'
import {ProfileRegistry} from '@/store/profiles/registry.ts'
import {FormRegistry} from '@/store/forms/registry.ts'
import {RegistryRegistry} from '@/store/registry-base.ts'

export interface ArtVueGlobals {
  _uid: string,
  // Store
  $store: ArtStore,
  // Socket
  $sock: SocketManager,
  // Shortcuts
  $displayImage: (asset: object, thumbName: string) => string,
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
