import Vue from 'vue'
import {setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import {genProduct, genUser} from '@/specs/helpers/fixtures'
import AcProductPreview from '@/components/AcProductPreview.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore

describe('AcProductPreview.ts', () => {
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
      AcProductPreview, {
        localVue,
        store,
        stubs: ['router-link'],
        propsData: {product: genProduct()},
        sync: false,
        attachToDocument: true,
      })
  })
})
