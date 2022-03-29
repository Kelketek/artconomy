import {BaseController} from '@/store/controller-base'
import Component from 'vue-class-component'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'
import CharacterState from '@/store/characters/types/CharacterState'
import Vue from 'vue'
import {characterEndpoint} from '@/store/characters/helpers'
import {SingleController} from '@/store/singles/controller'
import {Character} from '@/store/characters/types/Character'
import {ListController} from '@/store/lists/controller'
import Attribute from '@/types/Attribute'
import Color from '@/store/characters/types/Color'
import Submission from '@/types/Submission'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import {CharacterModule} from '@/store/characters/index'
import {Watch} from 'vue-property-decorator'

@Component
export class CharacterController extends BaseController<CharacterModuleOpts, CharacterState> {
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

  public setEndpoints() {
    const baseEndpoint = characterEndpoint(this.attr('username'), this.attr('characterName'))
    this.profile.endpoint = baseEndpoint
    this.attributes.endpoint = `${baseEndpoint}attributes/`
    this.colors.endpoint = `${baseEndpoint}colors/`
    this.submissions.endpoint = `${baseEndpoint}submissions/`
    this.sharedWith.endpoint = `${baseEndpoint}share/`
    this.recommended.endpoint = `${baseEndpoint}recommended/`
  }

  public kill() {
    // No-op for compatibility
  }

  public updateRoute(newName: string, oldName: string|undefined) {
    const username = this.$route.params.username
    if (username === undefined) {
      return
    }
    const characterName = this.$route.params.characterName
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
    const name = this.$route.name || undefined
    const route = {
      name,
      params: {...this.$route.params},
      query: {...this.$route.query},
      hash: this.$route.hash,
    }
    route.params.characterName = newName
    this.$router.replace(route)
  }

  @Watch('profile.x.name')
  public updateName(newName: string, oldName: string|undefined) {
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

  public created() {
    this.register()
    const baseEndpoint = characterEndpoint(this.attr('username'), this.attr('characterName'))
    Vue.set(this, 'profile', this.$getSingle(
      this.path.concat(['profile']).join('/'), {endpoint: ''},
    ))
    Vue.set(this, 'attributes', this.$getList(
      this.path.concat(['attributes']).join('/'), {endpoint: '', paginated: false},
    ))
    Vue.set(this, 'colors', this.$getList(
      this.path.concat(['colors']).join('/'), {endpoint: '', paginated: false},
    ))
    Vue.set(this, 'submissions', this.$getList(
      this.path.concat(['submissions']).join('/'), {endpoint: ''},
    ))
    Vue.set(this, 'sharedWith', this.$getList(
      this.path.concat(['sharedWith']).join('/'), {endpoint: '', paginated: false},
    ))
    Vue.set(this, 'recommended', this.$getList(
      this.path.concat(['recommended']).join('/'), {endpoint: '', params: {size: 6}},
    ))
    this.setEndpoints()
  }
}
