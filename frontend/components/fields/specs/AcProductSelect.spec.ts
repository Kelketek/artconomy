import {VueWrapper} from '@vue/test-utils'
import {mount, vueSetup} from '@/specs/helpers/index.ts'
import mockAxios from '@/__mocks__/axios.ts'
import AcProductSelect from '@/components/fields/AcProductSelect.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {describe, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

vi.useFakeTimers()
let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcProductSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      mockAxios.reset()
      vi.clearAllTimers()
    }
  })
  test('Calls a custom display handler', () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcProductSelect, {
        ...vueSetup({store}),
        props: {
          modelValue: 1,
          multiple: false,
          username: 'Fox',
          initItems: [{
            name: 'Test',
            id: 1,
            starting_price: 2.50,
          }, {
            username: 'Test2',
            id: 2,
            starting_price: 2.50,
          }],
        },
      },
    )
  })
})
