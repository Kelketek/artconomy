import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {afterEach, beforeEach, describe, test, vi} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

const mockError = vi.spyOn(console, 'error')

describe('AcMiniCharacter.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcMiniCharacter, {
        ...vueSetup({stubs: ['router-link']}),
        props: {character: genCharacter()},
      },
    )
  })
})
