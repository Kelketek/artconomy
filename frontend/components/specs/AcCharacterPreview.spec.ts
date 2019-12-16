import Vue from 'vue'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('AcCharacterPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcCharacterPreview, {
        localVue,
        store,
        vuetify,
        stubs: ['router-link'],
        propsData: {character: genCharacter()},
        sync: false,
        attachToDocument: true,
      })
  })
})
