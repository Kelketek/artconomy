import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genUser} from '@/specs/helpers/fixtures'
import {afterEach, beforeEach, describe, test} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcCharacterPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcCharacterPreview, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {character: genCharacter()},
      })
  })
})
