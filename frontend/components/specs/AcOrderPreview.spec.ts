import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genOrder, genUser} from '@/specs/helpers/fixtures.ts'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Order from '@/types/Order.ts'
import {afterEach, beforeEach, describe, expect, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

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
