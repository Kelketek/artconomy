import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import {genOrder, genUser} from '@/specs/helpers/fixtures'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore
let order: SingleController<Order>

describe('AcOrderPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
    setViewer(store, genUser())
    order = mount(Empty, vueSetup({store})).vm.$getSingle('order', {
      endpoint: '#',
      x: genOrder(),
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Identifies whether the user is the buyer', async() => {
    wrapper = mount(
      AcOrderPreview, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {
          order,
          username: 'Fox',
          type: 'Sale',
        },
      })
    const vm = wrapper.vm as any
    expect(vm.isBuyer).toBe(true)
    setViewer(store, genUser({username: 'Vulpes'}))
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
  })
})
