import Vue from 'vue'
import {setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import ProductHints from '@/components/views/search/hints/ProductHints.vue'
import searchSchema from '@/components/views/search/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore

describe('ProductHints.vue', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Performs a search', async() => {
    wrapper = mount(ProductHints, {localVue, store})
    wrapper.find('.v-chip__content').trigger('click')
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe('refsheet')
  })
})
