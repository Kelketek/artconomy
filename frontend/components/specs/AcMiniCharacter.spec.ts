import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcMiniCharacter.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcMiniCharacter, {
        store,
        localVue,
        vuetify,

        attachTo: docTarget(),
        propsData: {character: genCharacter()},
        stubs: ['router-link'],
      },
    )
  })
})
