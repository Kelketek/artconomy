import {VueWrapper} from '@vue/test-utils'
import Editable from '@/specs/helpers/dummy_components/editable.vue'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

const mockError = vi.spyOn(console, 'error')

describe('Editable.ts', () => {
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    vueSetup()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Reports when editing', async() => {
    const replace = vi.fn()
    wrapper = mount(
      Editable, {
        props: {controls: true},
        ...vueSetup({mocks: {$router: {replace}, $route: {query: {editing: "true"}}}}),
      },
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(true)
  })
  test('Reports when not editing', async() => {
    const replace = vi.fn()
    wrapper = mount(
      Editable, {
        props: {controls: true},
        ...vueSetup({mocks: {$router: {replace}, $route: {query: {}}}}),
      },
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(false)
  })
  test('Reports not editing if controls is false', async() => {
    const replace = vi.fn()
    wrapper = mount(
      Editable, {
        props: {controls: false},
        ...vueSetup({mocks: {$router: {replace}, $route: {query: {editing: "true"}}}}),
      },
    )
    const vm = wrapper.vm as any
    expect(vm.editing).toBe(false)
  })
  test('Locks the view', async() => {
    const replace = vi.fn()
    wrapper = mount(
      Editable, {
        props: {controls: true},
        ...vueSetup({mocks: {$router: {replace}, $route: {query: {editing: "true", what: 'things'}}}}),
      },
    )
    const vm = wrapper.vm as any
    vm.editing = false
    expect(replace).toHaveBeenCalledWith({query: {what: 'things'}})
  })
  test('Unlocks the view', async() => {
    const replace = vi.fn()
    wrapper = mount(
      Editable, {
        props: {controls: true},
        ...vueSetup({mocks: {$router: {replace}, $route: {query: {what: 'things'}}}}),
      },
    )
    const vm = wrapper.vm as any
    vm.editing = true
    expect(replace).toHaveBeenCalledWith({query: {what: 'things', editing: "true"}})
  })
})
