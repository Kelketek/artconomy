import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'
import {ListController} from '@/store/lists/controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import VueObserveVisibilityPlugin from 'vue-observe-visibility'

let vuetify: Vuetify
let store: ArtStore
let localVue = vueSetup()
localVue.use(VueObserveVisibilityPlugin)
let list: ListController<any>
let wrapper: Wrapper<Vue>

describe('AcGrowSpinner.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Runs the grower', async() => {
    list = mount(Empty, {localVue, store, vuetify, sync: false}).vm.$getList('stuff', {
      endpoint: '/', grow: true,
    })
    const mockWarn = jest.spyOn(console, 'warn')
    mockWarn.mockImplementationOnce(() => undefined)
    wrapper = mount(AcGrowSpinner, {localVue, store, vuetify, sync: false, attachToDocument: true, propsData: {list}})
    expect(list.fetching).toBe(false)
    const vm = wrapper.vm as any
    vm.visible = true
    list.response = {
      count: 30,
      size: 10,
    }
    await vm.$nextTick()
    expect(list.fetching).toBe(true)
  })
})
