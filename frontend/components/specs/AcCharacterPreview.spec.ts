import Vue from 'vue'
import {setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore

describe('AcCharacterPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', () => {
    setViewer(store, genUser())
    wrapper = mount(
      AcCharacterPreview, {
        localVue,
        store,
        stubs: ['router-link'],
        propsData: {character: genCharacter()},
        sync: false,
        attachToDocument: true,
      })
  })
})
