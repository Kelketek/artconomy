import {VueWrapper} from '@vue/test-utils'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {afterEach, beforeEach, describe, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

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
