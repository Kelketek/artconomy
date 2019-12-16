import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import ProductHints from '@/components/views/search/hints/ProductHints.vue'
import searchSchema from '@/components/views/search/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('ProductHints.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    setViewer(store, genUser())
    mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Performs a search', async() => {
    wrapper = mount(ProductHints, {localVue, store, vuetify})
    wrapper.find('.v-chip__content').trigger('click')
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe('refsheet')
  })
})
