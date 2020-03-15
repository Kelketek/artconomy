import {cleanUp, createVuetify, flushPromises, rs, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {deliverableRouter} from '@/components/views/order/specs/helpers'
import {genDeliverable, genReference, genUser} from '@/specs/helpers/fixtures'
import mockAxios from '@/__mocks__/axios'
import {genCharacter} from '@/store/characters/specs/fixtures'
import DeliverableReferences from '@/components/views/order/deliverable/DeliverableReferences.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('DeliverableReferences.vue', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    store = createStore()
    vuetify = createVuetify()
    router = deliverableRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Adds character tags to submission form', async() => {
    setViewer(store, genUser())
    router.push('/orders/Fox/order/1/deliverables/5')
    wrapper = mount(
      DeliverableReferences, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      })
    const vm = wrapper.vm as any
    vm.deliverable.setX(genDeliverable())
    vm.deliverable.fetching = false
    vm.deliverable.ready = true
    vm.fetching = false
    vm.revisions.setList([])
    vm.revisions.fetching = false
    vm.revisions.ready = true
    const characterRequest = mockAxios.getReqByUrl('/api/sales/v1/order/1/deliverables/5/characters/')
    const character = genCharacter()
    character.tags = ['stuff', 'things', 'wat']
    mockAxios.mockResponse(rs([{id: 1, character}]), characterRequest)
    await flushPromises()
    await vm.$nextTick()
    expect([...vm.addSubmission.fields.tags.value].sort()).toEqual(['stuff', 'things', 'wat'])
  })
  it('Autosubmits a reference when a new file is added', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    router.push('/orders/Fox/order/1/deliverables/5/references')
    wrapper = mount(
      DeliverableReferences, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 1, deliverableId: 5, baseName: 'Order', username: 'Fox'},
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    const spySubmit = jest.spyOn(vm.newReference, 'submitThen')
    const spyPost = jest.spyOn(vm.references, 'post')
    const deliverable = genDeliverable()
    expect(vm.references.list.length).toBe(0)
    vm.order.makeReady(deliverable.order)
    vm.deliverable.makeReady(deliverable)
    vm.references.setList([])
    vm.references.ready = true
    vm.references.fetching = false
    await vm.$nextTick()
    mockAxios.reset()
    vm.newReference.fields.file.update('Stuff')
    await vm.$nextTick()
    expect(spySubmit).toHaveBeenCalledWith(expect.any(Function))
    const reference = genReference()
    mockAxios.mockResponse(rs(reference))
    await flushPromises()
    await vm.$nextTick()
    expect(spyPost).toHaveBeenCalledWith({reference_id: reference.id})
    mockAxios.mockResponse(rs(reference))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.references.list.length).toBe(1)
  })
})
