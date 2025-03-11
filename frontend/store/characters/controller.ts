import {BaseController, ControllerArgs} from '@/store/controller-base.ts'
import {characterEndpoint} from '@/store/characters/helpers.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {CharacterModule} from '@/store/characters/index.ts'
import {ComputedGetters} from '@/lib/lib.ts'
import {toValue, watch} from 'vue'
import {getController} from '@/store/registry-base.ts'
import type {Attribute, Submission} from '@/types/main'
import type {SingleModuleOpts, SingleState} from '@/store/singles/types.d.ts'
import {TerseUser} from '@/store/profiles/types/main'
import type {ListModuleOpts, ListState} from '@/store/lists/types.d.ts'
import type {Character, CharacterModuleOpts, CharacterState, Color} from '@/store/characters/types/main'

@ComputedGetters
export class CharacterController extends BaseController<CharacterModuleOpts, CharacterState> {
  public __getterMap = new Map()
  public profile: SingleController<Character> = null as unknown as SingleController<Character>
  public attributes: ListController<Attribute> = null as unknown as ListController<Attribute>
  public colors: ListController<Color> = null as unknown as ListController<Color>
  public submissions: ListController<Submission> = null as unknown as ListController<Submission>
  public sharedWith: ListController<TerseUser> = null as unknown as ListController<TerseUser>
  public recommended: ListController<Character> = null as unknown as ListController<Character>
  public submoduleKeys = ['profile', 'attributes', 'colors', 'submissions', 'sharedWith', 'recommended']
  public baseClass = CharacterModule
  public baseModuleName = 'characterModules'
  public typeName = 'Character' as const

  public constructor(args: ControllerArgs<CharacterModuleOpts>) {
    super(args)
    this.register()
    this.profile = getController<SingleState<Character>, SingleModuleOpts<Character>, SingleController<Character>>(
      {
        uid: this._uid,
        name: this.path.concat(['profile']).join('/'),
        typeName: 'Single',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {endpoint: ''},
        registries: this.$registries,
        ControllerClass: SingleController,
      },
    )
    this.attributes = getController<ListState<Attribute>, ListModuleOpts, ListController<Attribute>>(
      {
        uid: this._uid,
        name: this.path.concat(['attributes']).join('/'),
        typeName: 'List',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {
          endpoint: '',
          paginated: false,
        },
        registries: this.$registries,
        ControllerClass: ListController,
      },
    )
    this.colors = getController<ListState<Color>, ListModuleOpts, ListController<Color>>(
      {
        uid: this._uid,
        name: this.path.concat(['colors']).join('/'),
        typeName: 'List',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {
          endpoint: '',
          paginated: false,
        },
        registries: this.$registries,
        ControllerClass: ListController,
      },
    )
    this.submissions = getController<ListState<Submission>, ListModuleOpts, ListController<Submission>>(
      {
        uid: this._uid,
        name: this.path.concat(['submissions']).join('/'),
        typeName: 'List',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {endpoint: ''},
        registries: this.$registries,
        ControllerClass: ListController,
      },
    )
    this.sharedWith = getController<ListState<TerseUser>, ListModuleOpts, ListController<TerseUser>>(
      {
        uid: this._uid,
        name: this.path.concat(['sharedWith']).join('/'),
        typeName: 'List',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {
          endpoint: '',
          paginated: false,
        },
        registries: this.$registries,
        ControllerClass: ListController,
      },
    )
    this.recommended = getController<ListState<Character>, ListModuleOpts, ListController<Character>>(
      {
        uid: this._uid,
        name: this.path.concat(['recommended']).join('/'),
        typeName: 'List',
        router: this.$router,
        socket: this.$sock,
        store: this.$store,
        schema: {
          endpoint: '',
          params: {size: 6},
        },
        registries: this.$registries,
        ControllerClass: ListController,
      },
    )
    this.setEndpoints()
    watch(() => this.profile.x?.name || '', this.updateName)
  }

  public setEndpoints = () => {
    const baseEndpoint = characterEndpoint(this.attr('username'), this.attr('characterName'))
    this.profile.endpoint = baseEndpoint
    this.attributes.endpoint = `${baseEndpoint}attributes/`
    this.colors.endpoint = `${baseEndpoint}colors/`
    this.submissions.endpoint = `${baseEndpoint}submissions/`
    this.sharedWith.endpoint = `${baseEndpoint}share/`
    this.recommended.endpoint = `${baseEndpoint}recommended/`
  }

  public kill = () => {
    // No-op for compatibility
  }

  public updateRoute = (newName: string, oldName: string | undefined) => {
    const currentRoute = toValue(this.$router.currentRoute)
    const username = currentRoute.params.username
    if (username === undefined) {
      return
    }
    const characterName = currentRoute.params.characterName
    if (characterName === undefined) {
      return
    }
    if (username !== this.attr('username')) {
      return
    }
    if (characterName !== oldName) {
      return
    }
    /* istanbul ignore next */
    const name = currentRoute.name || undefined
    const route = {
      name,
      params: {...currentRoute.params},
      query: {...currentRoute.query},
      hash: currentRoute.hash,
    }
    route.params.characterName = newName
    return this.$router.replace(route)
  }

  // Watcher for profile.x.name
  public updateName = (newName: string, oldName: string | undefined) => {
    if (this.attr('characterName') === newName) {
      // Initial load. Ignore.
      return
    }
    /* istanbul ignore if */
    if (!newName) {
      // Destroying instance. No need to make changes.
      return
    }
    const newPath = [...this.path]
    newPath[newPath.length - 1] = newName
    this.migrate(newPath.join('/'))
    this.setEndpoints()
    this.updateRoute(newName, oldName)
  }
}
