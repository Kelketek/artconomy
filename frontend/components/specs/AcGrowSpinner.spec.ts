import {ArtStore, createStore} from '@/store'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import AcGrowSpinner from '@/components/AcGrowSpinner.vue'
import {ListController} from '@/store/lists/controller'
import Empty from '@/specs/helpers/dummy_components/empty'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

let store: ArtStore
let list: ListController<any>
let wrapper: VueWrapper<any>

describe('AcGrowSpinner.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Runs the grower', async() => {
    list = mount(Empty, vueSetup({store})).vm.$getList('stuff', {
      endpoint: '/',
      grow: true,
    })
    const mockWarn = vi.spyOn(console, 'warn')
    mockWarn.mockImplementationOnce(() => undefined)
    wrapper = mount(AcGrowSpinner, {
      ...vueSetup({store}),
      props: {list},
    })
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
