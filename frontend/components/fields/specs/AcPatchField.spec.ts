import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, rq, rs, vueSetup, VuetifyWrapped} from '@/specs/helpers/index.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {SingleController} from '@/store/singles/controller.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {nextTick} from 'vue'
import flushPromises from 'flush-promises'

let store: ArtStore
let wrapper: VueWrapper<any>
let single: SingleController<any>
let empty: VueWrapper<any>

const WrappedAcPatchField = VuetifyWrapped(AcPatchField)

describe('AcPatchField.ts', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    empty = mount(Empty, vueSetup({store}))
    single = empty.vm.$getSingle('stuff', {endpoint: '/'})
    single.setX({test: 'Things'})
    store.commit('singles/stuff/setReady', true)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Creates a field based on a patch', async() => {
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#stuff-patch').exists()).toBe(true)
  })
  test('Sends an update upon pressing enter when enterSave is true', async() => {
    wrapper = mount(WrappedAcPatchField, {
      ...vueSetup({store}),
      props: {patcher: single.patchers.test, id: 'stuff-patch', enterSave: true},
    })
    const field = wrapper.find('#stuff-patch')
    await field.setValue('TEST')
    await field.trigger('keydown.enter')
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/', 'patch', {test: 'TEST'}, {signal: expect.any(Object)}),
    )
    mockAxios.mockResponse(rs({test: 'TEST'}))
    await flushPromises()
  })
  test('Does not patch on enter keydown when enterSave is false', async() => {
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
        enterSave: false,
        autoSave: false,
      },
    })
    const field = wrapper.find('#stuff-patch')
    await field.setValue('TEST')
    await field.trigger('keydown.enter')
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    expect(mockAxios.request).not.toHaveBeenCalled()
  })
  test('Recognizes disparate types as an indication that things are not saved', async() => {
    single.setX({test: null})
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
        autoSave: false,
      },
    })
    const field = wrapper.find('#stuff-patch')
    await field.setValue('STUFF')
    await wrapper.vm.$nextTick()
    vi.runAllTimers()
    const vm = wrapper.vm as any
    expect(vm.saved).toBe(false)
  })
  test('Updates from upstream when handlesSaving is true even if autoSave is false', async() => {
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
        fieldType: 'ac-editor',
        autoSave: false,
        handlesSaving: true,
      },
    })
    single.patchers.test.model = 'TEST'
    await nextTick()
    const vm = wrapper.vm as any
    expect(vm.scratch).toBe('TEST')
  })
  test('Identifies object equality', async() => {
    single.updateX({test: {stuff: 'things'}})
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
        autoSave: false,
        handlesSaving: true,
      },
    })
    const vm = wrapper.vm as any
    vm.scratch = {stuff: 'things'}
    await vm.$nextTick()
    expect(vm.saved).toBe(true)
    vm.scratch = {stuff: 'Wat'}
    await vm.$nextTick()
    expect(vm.saved).toBe(false)
  })
  test('Handles numeric equality', async() => {
    single.updateX({test: 10.10})
    wrapper = mount(AcPatchField, {
      ...vueSetup({store}),
      props: {
        patcher: single.patchers.test,
        id: 'stuff-patch',
        autoSave: false,
        handlesSaving: true,
      },
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
