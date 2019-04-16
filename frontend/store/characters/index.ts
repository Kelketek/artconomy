import {ActionTree, GetterTree, MutationTree} from 'vuex'
import {UserStoreState} from '@/store/profiles/types/UserStoreState'
import CharacterState from '@/store/characters/types/CharacterState'
import CharacterModuleOpts from '@/store/characters/types/CharacterModuleOpts'

export class CharacterModule {
  public state: CharacterState
  public mutations: MutationTree<CharacterState>
  public actions: ActionTree<CharacterState, UserStoreState>
  public getters: GetterTree<CharacterState, UserStoreState>
  public namespaced = true
  constructor(schema: CharacterModuleOpts) {
    const defaults = {persistent: false}
    this.mutations = {}
    this.actions = {}
    // Actual creation of the relevant singles will happen outside of this module.
    this.state = {...defaults, ...schema}
    this.getters = {}
  }
}

export const characterModules = {
  namespaced: true,
  state: () => ({}),
  getters: {},
  actions: {},
  mutations: {},
}
