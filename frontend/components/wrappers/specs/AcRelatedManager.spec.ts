import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import mockAxios from '@/__mocks__/axios'
import {cleanUp, createVuetify, docTarget, flushPromises, rq, rs, vueSetup, mount} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import DummyRelated from '@/components/wrappers/specs/DummyRelated.vue'
import Vuetify from 'vuetify/lib'

describe('AcRelatedManager.vue', () => {
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let vuetify: Vuetify
  const localVue = vueSetup()
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads up related items', async() => {
    wrapper = mount(DummyRelated, {
      localVue,
      store,
      vuetify,

      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: expect.any(Object)}),
    )
    const user1 = genUser()
    user1.id = 1
    user1.username = 'Fox'
    const user2 = genUser()
    user2.id = 2
    user2.username = 'Vulpes'
    mockAxios.mockResponse(rs([{user: user1, id: 1}, {user: user2, id: 2}]))
    await wrapper.vm.$nextTick()
  })
  it('Filters existing items out of results', async() => {
    wrapper = mount(DummyRelated, {
      localVue,
      store,
      vuetify,

      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: expect.any(Object)}),
    )
    const user1 = genUser()
    user1.id = 1
    user1.username = 'Fox'
    const user2 = genUser()
    user2.id = 2
    user2.username = 'Vulpes'
    const user3 = genUser()
    user3.id = 3
    user3.username = 'Terrence'
    mockAxios.mockResponse(rs([{user: user1, id: 1}, {user: user2, id: 2}]))
    await flushPromises()
    const vm = wrapper.vm as any
    expect(vm.$refs.manager.filter(user1, 'Fox', user1.username)).toBe(false)
    expect(vm.$refs.manager.filter(user3, 'Ter', user3.username)).toBe(true)
    expect(vm.$refs.manager.filter(user2, 'Bob', user2.username)).toBe(false)
    expect(vm.$refs.manager.filter(user3, '', user3.username)).toBe(false)
  })
  it('Auto-submits when the bound field is updated.', async() => {
    wrapper = mount(DummyRelated, {
      localVue,
      store,
      vuetify,

      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: expect.any(Object)}),
    )
    mockAxios.reset()
    const vm = wrapper.vm as any
    vm.userForm.fields.user_id.update(3)
    await vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'post', {user_id: 3}, {}),
    )
    const user = genUser()
    user.id = 3
    const relation = {user, id: 4}
    mockAxios.mockResponse(rs(relation))
    await flushPromises()
    expect(vm.demoList.list[0].x).toEqual(relation)
  })
})
