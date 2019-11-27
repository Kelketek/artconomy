import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {rq, rs, vuetifySetup} from '@/specs/helpers'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {singleRegistry, Singles} from '@/store/singles/registry'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {SingleController} from '@/store/singles/controller'
import mockAxios from '@/__mocks__/axios'

jest.useFakeTimers()
Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
let store: ArtStore
let wrapper: Wrapper<Vue>
let single: SingleController<any>
let empty: Wrapper<Vue>

describe('AcPatchField.ts', () => {
  beforeEach(() => {
    vuetifySetup()
    singleRegistry.reset()
    store = createStore()
    mockAxios.reset()
    if (wrapper) {
      wrapper.destroy()
    }
    empty = mount(Empty, {localVue, store, sync: false})
    single = empty.vm.$getSingle('stuff', {endpoint: '/'})
    single.setX({test: 'Things'})
    store.commit('singles/stuff/setReady', true)
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    empty.destroy()
  })
  it('Creates a field based on a patch', async() => {
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#stuff-patch').exists()).toBe(true)
  })
  it('Sends an update upon pressing enter when enterSave is true', async() => {
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', enterSave: true},
    })
    const field = wrapper.find('#stuff-patch')
    field.setValue('TEST')
    field.trigger('keydown.enter')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    expect(mockAxios.patch).toHaveBeenCalledWith(
      ...rq('/', 'patch', {test: 'TEST'}, {cancelToken: {}})
    )
    mockAxios.mockResponse(rs({test: 'TEST'}))
  })
  it('Does not patch on enter keydown when enterSave is false', async() => {
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', enterSave: false, autoSave: false},
    })
    const field = wrapper.find('#stuff-patch')
    field.setValue('TEST')
    field.trigger('keydown.enter')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    expect(mockAxios.patch).not.toHaveBeenCalled()
  })
  it('Resets the saved value on failure if autoSave is false', async() => {
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', autoSave: false},
    })
    const field = wrapper.find('#stuff-patch')
    field.setValue('TEST')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    const vm = wrapper.vm as any
    expect(vm.scratch).toBe('TEST')
    single.patchers.test.errors = ['Boop.']
    await vm.$nextTick()
    expect(vm.scratch).toBe('Things')
  })
  it('Recognizes disparate types as an indication that things are not saved', async() => {
    single.setX({test: null})
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', autoSave: false},
    })
    const field = wrapper.find('#stuff-patch')
    field.setValue('STUFF')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    const vm = wrapper.vm as any
    expect(vm.saved).toBe(false)
  })
  it('Updates from upstream when handlesSaving is true even if autoSave is false', async() => {
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', autoSave: false, handlesSaving: true},
    })
    single.patchers.test.model = 'TEST'
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.scratch).toBe('TEST')
  })
  it('Identifies object equality', async() => {
    single.updateX({test: {stuff: 'things'}})
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', autoSave: false, handlesSaving: true},
    })
    const vm = wrapper.vm as any
    vm.scratch = {stuff: 'things'}
    await vm.$nextTick()
    expect(vm.saved).toBe(true)
    vm.scratch = {stuff: 'Wat'}
    await vm.$nextTick()
    expect(vm.saved).toBe(false)
  })
  it('Handles numeric equality', async() => {
    single.updateX({test: 10.10})
    wrapper = mount(AcPatchField, {
      localVue,
      store,
      sync: false,
      attachToDocument: true,
      propsData: {patcher: single.patchers.test, id: 'stuff-patch', autoSave: false, handlesSaving: true},
    })
    const vm = wrapper.vm as any
    vm.scratch = '10.100'
    await vm.$nextTick()
    expect(vm.saved).toBe(true)
    vm.scratch = {stuff: '10'}
    await vm.$nextTick()
    expect(vm.saved).toBe(false)
  })
})
