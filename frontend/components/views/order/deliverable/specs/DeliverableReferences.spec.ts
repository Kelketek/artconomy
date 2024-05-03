import {cleanUp, flushPromises, mount, rs, vueSetup} from '@/specs/helpers/index.ts'
import {Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {deliverableRouter} from '@/components/views/order/specs/helpers.ts'
import {genDeliverable, genReference, genUser} from '@/specs/helpers/fixtures.ts'
import mockAxios from '@/__mocks__/axios.ts'
import DeliverableReferences from '@/components/views/order/deliverable/DeliverableReferences.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('DeliverableReferences.vue', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    store = createStore()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Autosubmits a reference when a new file is added', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/deliverables/5/references')
    wrapper = mount(
      DeliverableReferences, {
        ...vueSetup({
          store,
          router,
        }),
        props: {
          orderId: 1,
          deliverableId: 5,
          baseName: 'Order',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm as any
    const spySubmit = vi.spyOn(vm.newReference, 'submitThen')
    const spyPost = vi.spyOn(vm.references, 'post')
    const deliverable = genDeliverable()
    expect(vm.references.list.length).toBe(0)
    vm.deliverable.makeReady(deliverable)
    vm.references.makeReady([])
    vm.references.ready = true
    await vm.$nextTick()
    await flushPromises()
    mockAxios.reset()
    vm.newReference.fields.file.update('Stuff')
    await vm.$nextTick()
    expect(spySubmit).toHaveBeenCalledWith(expect.any(Function))
    const reference = genReference()
    mockAxios.mockResponse(rs(reference))
    await flushPromises()
    await vm.$nextTick()
    expect(spyPost).toHaveBeenCalledWith({reference_id: reference.id})
    mockAxios.mockResponse(rs({reference, deliverable_id: deliverable.id}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.references.list.length).toBe(1)
  })
})
