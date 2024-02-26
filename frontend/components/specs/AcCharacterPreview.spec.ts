import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {afterEach, beforeEach, describe, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

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
