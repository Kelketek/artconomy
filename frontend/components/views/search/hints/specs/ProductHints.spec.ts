import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import ProductHints from '@/components/views/search/hints/ProductHints.vue'
import searchSchema from '@/components/views/search/specs/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('ProductHints.vue', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Performs a search', async() => {
    wrapper = mount(ProductHints, vueSetup({store}))
    await wrapper.find('.v-chip__content').trigger('click')
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe('refsheet')
  })
})
