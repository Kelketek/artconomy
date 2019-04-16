import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser, vuetifyOptions} from '@/specs/helpers/fixtures'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuex)
Vue.use(Vuetify, vuetifyOptions())
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let wrapper: Wrapper<Vue>
let store: ArtStore

const mockError = jest.spyOn(console, 'error')

describe('AcMiniCharacter.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    profileRegistry.reset()
    mockError.mockClear()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcMiniCharacter, {
        store,
        localVue,
        sync: false,
        attachToDocument: true,
        propsData: {character: genCharacter()},
        stubs: ['router-link'],
      }
    )
  })
})
