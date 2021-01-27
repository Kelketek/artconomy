import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, qMount, vueSetup, mount} from '@/specs/helpers'
import AcBirthdayField from '@/components/fields/AcBirthdayField.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcBirthdayField.vue', () => {
  beforeEach(() => {
    store = createStore()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Creates a datepicker in year mode by default.', async() => {
    wrapper = qMount(AcBirthdayField, {localVue, store, propsData: {value: null}})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.menu = true
    await vm.$nextTick()
    jest.runAllTimers()
    await vm.$nextTick()
    expect(vm.$refs.picker.activePicker).toBe('YEAR')
  })
  it('Sends an updated value.', async() => {
    wrapper = qMount(AcBirthdayField, {localVue, store, propsData: {value: null}})
    const vm = wrapper.vm as any
    const mockEmit = jest.spyOn(vm, '$emit')
    await vm.$nextTick()
    vm.scratch = '1988-08-01'
    await vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', '1988-08-01')
  })
})
