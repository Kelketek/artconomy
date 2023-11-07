import {BaseController, ControllerArgs} from '@/store/controller-base'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'
import CharacterState from '@/store/characters/types/CharacterState'
import {characterEndpoint} from '@/store/characters/helpers'
import {SingleController} from '@/store/singles/controller'
import {Character} from '@/store/characters/types/Character'
import {ListController} from '@/store/lists/controller'
import Attribute from '@/types/Attribute'
import Color from '@/store/characters/types/Color'
import Submission from '@/types/Submission'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {CharacterModule} from '@/store/characters/index'
import {ComputedGetters} from '@/lib/lib'
import {watch} from 'vue'

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
  public typeName = 'Character'

  public constructor(args: ControllerArgs<CharacterModuleOpts>) {
    super(args)
    this.register()
    this.profile = this.$root.$getSingle(
      this.path.concat(['profile']).join('/'), {endpoint: ''}, this._uid,
    )
    this.attributes = this.$root.$getList(
      this.path.concat(['attributes']).join('/'), {endpoint: '', paginated: false}, this._uid,
    )
    this.colors = this.$root.$getList(
      this.path.concat(['colors']).join('/'), {endpoint: '', paginated: false}, this._uid,
    )
    this.submissions = this.$root.$getList(
      this.path.concat(['submissions']).join('/'), {endpoint: ''}, this._uid,
    )
    this.sharedWith = this.$root.$getList(
      this.path.concat(['sharedWith']).join('/'), {endpoint: '', paginated: false}, this._uid,
    )
    this.recommended = this.$root.$getList(
      this.path.concat(['recommended']).join('/'), {endpoint: '', params: {size: 6}}, this._uid,
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

  public updateRoute = (newName: string, oldName: string|undefined) => {
    const username = this.$root.$route.params.username
    if (username === undefined) {
      return
    }
    const characterName = this.$root.$route.params.characterName
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
    const name = this.$root.$route.name || undefined
    const route = {
      name,
      params: {...this.$root.$route.params},
      query: {...this.$root.$route.query},
      hash: this.$root.$route.hash,
    }
    route.params.characterName = newName
    this.$root.$router.replace(route)
  }

  // Watcher for profile.x.name
  public updateName = (newName: string, oldName: string|undefined) => {
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
