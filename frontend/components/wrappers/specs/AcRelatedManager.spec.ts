import Vue from 'vue'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import {ArtStore, createStore} from '@/store'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import mockAxios from '@/__mocks__/axios'
import {FormControllers} from '@/store/forms/registry'
import {flushPromises, rq, rs, vuetifySetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import DummyRelated from '@/components/wrappers/specs/DummyRelated.vue'

Vue.use(Vuetify)
Vue.use(Vuex)

describe('AcRelatedManager.vue', () => {
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  const localVue = createLocalVue()
  localVue.use(Singles)
  localVue.use(Lists)
  localVue.use(FormControllers)
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Loads up related items', async() => {
    wrapper = mount(DummyRelated, {localVue, store, sync: false, stubs: ['router-link'], attachToDocument: true})
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: {}})
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
    wrapper = mount(DummyRelated, {localVue, store, sync: false, stubs: ['router-link'], attachToDocument: true})
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: {}})
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
    wrapper = mount(DummyRelated, {localVue, store, sync: false, stubs: ['router-link'], attachToDocument: true})
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'get', undefined, {cancelToken: {}})
    )
    mockAxios.reset()
    const vm = wrapper.vm as any
    vm.userForm.fields.user_id.update(3)
    await vm.$nextTick()
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/endpoint/', 'post', {user_id: 3}, {})
    )
    const user = genUser()
    user.id = 3
    const relation = {user, id: 4}
    mockAxios.mockResponse(rs(relation))
    await flushPromises()
    expect(vm.demoList.list[0].x).toEqual(relation)
  })
})
