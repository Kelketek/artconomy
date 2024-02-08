import {VueWrapper} from '@vue/test-utils'
import {cleanUp, flushPromises, mount, rs, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import AcCharacterSelect from '@/components/fields/AcCharacterSelect.vue'
import mockAxios from '@/__mocks__/axios.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

vi.useFakeTimers()
let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcCharacterSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    vi.clearAllTimers()
    cleanUp(wrapper)
  })
  test('Accepts a response from the server on its query', async() => {
    setViewer(store, genUser())
    const tagList: number[] = []
    wrapper = mount(AcCharacterSelect, {
      ...vueSetup({store}),
      props: {modelValue: tagList},
    })
    wrapper.vm.query = 'Test'
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    mockAxios.mockResponse(rs({
        results: [
          {
            name: 'Test',
            id: 1,
            user: {username: 'Fox'},
          },
          {
            name: 'Test2',
            id: 2,
            user: {username: 'Dude'},
          },
        ],
      },
    ))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).items).toEqual([
      {
        name: 'Test',
        id: 1,
        user: {username: 'Fox'},
      },
      {
        name: 'Test2',
        id: 2,
        user: {username: 'Dude'},
      },
    ])
  })
})
