import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genProduct, genUser} from '@/specs/helpers/fixtures.ts'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {afterEach, beforeEach, describe, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcProductPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', () => {
    setViewer({ store, user: genUser() })
    wrapper = mount(
      AcProductPreview, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {product: genProduct()},
      })
  })
})
