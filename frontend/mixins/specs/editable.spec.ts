import {createLocalVue, shallowMount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Editable from '@/specs/helpers/dummy_components/editable.vue'

const mockError = jest.spyOn(console, 'error')

describe('Editable.ts', () => {
  const localVue = createLocalVue()
  let wrapper: Wrapper<Vue> | null
  beforeEach(() => {
    wrapper = null
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Reports when editing', async() => {
    const replace = jest.fn()
    wrapper = shallowMount(
      Editable, {
        localVue,
        propsData: {controls: true},
        mocks: {$router: {replace}, $route: {query: {editing: true}}},
        sync: false}
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(true)
  })
  it('Reports when not editing', async() => {
    const replace = jest.fn()
    wrapper = shallowMount(
      Editable, {
        localVue,
        propsData: {controls: true},
        mocks: {$router: {replace}, $route: {query: {}}},
        sync: false}
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(false)
  })
  it('Reports not editing if controls is false', async() => {
    const replace = jest.fn()
    wrapper = shallowMount(
      Editable, {
        localVue,
        propsData: {controls: false},
        mocks: {$router: {replace}, $route: {query: {editing: true}}},
        sync: false}
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(false)
  })
  it('Locks the view', async() => {
    const replace = jest.fn()
    wrapper = shallowMount(
      Editable, {
        localVue,
        propsData: {controls: true},
        mocks: {$router: {replace}, $route: {query: {editing: true, what: 'things'}}},
        sync: false}
    )
    const vm = wrapper.vm as any
    vm.editing = false
    expect(replace).toHaveBeenCalledWith({query: {what: 'things'}})
  })
  it('Unlocks the view', async() => {
    const replace = jest.fn()
    wrapper = shallowMount(
      Editable, {
        localVue,
        propsData: {controls: true},
        mocks: {$router: {replace}, $route: {query: {what: 'things'}}},
        sync: false}
    )
    const vm = wrapper.vm as any
    vm.editing = true
    expect(replace).toHaveBeenCalledWith({query: {what: 'things', editing: true}})
  })
})
