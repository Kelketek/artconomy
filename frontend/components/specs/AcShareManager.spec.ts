import {vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {singleRegistry} from '@/store/singles/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {listRegistry} from '@/store/lists/registry'
import AcShareManager from '@/components/AcShareManager.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore

describe('AcShareManager.vue', () => {
  beforeEach(() => {
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    const list = mount(Empty, {localVue, store}).vm.$getList('stuff', {endpoint: '/'})
    wrapper = mount(AcShareManager, {
      localVue,
      store,
      propsData: {controller: list},
      sync: false,
      attachToDocument: true,
      stubs: ['ac-bound-field'],
    })
  })
})
