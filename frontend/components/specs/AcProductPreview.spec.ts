import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import {genProduct, genUser} from '@/specs/helpers/fixtures'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {afterEach, beforeEach, describe, test} from 'vitest'

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
    setViewer(store, genUser())
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
