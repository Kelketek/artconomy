import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {cleanUp, docTarget, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import DummyRelated from '@/components/wrappers/specs/DummyRelated.vue'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'

describe('AcRelatedManager.vue', () => {
  let wrapper: VueWrapper<any>
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Loads up related items', async() => {
    wrapper = mount(DummyRelated, vueSetup({
      store,
      stubs: ['router-link'],
    }))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/endpoint/', 'get', undefined, {signal: expect.any(Object)}),
    )
    const user1 = genUser()
    user1.id = 1
    user1.username = 'Fox'
    const user2 = genUser()
    user2.id = 2
    user2.username = 'Vulpes'
    mockAxios.mockResponse(rs([{
      user: user1,
      id: 1,
    }, {
      user: user2,
      id: 2,
    }]))
    await wrapper.vm.$nextTick()
  })
  // test('Filters existing items out of results', async() => {
  //   wrapper = mount(DummyRelated, vueSetup({
  //     store,
  //     stubs: ['router-link'],
  //   }))
  //   expect(mockAxios.request).toHaveBeenCalledWith(
  //     rq('/endpoint/', 'get', undefined, {signal: expect.any(Object)}),
  //   )
  //   const user1 = genUser()
  //   user1.id = 1
  //   user1.username = 'Fox'
  //   const user2 = genUser()
  //   user2.id = 2
  //   user2.username = 'Vulpes'
  //   const user3 = genUser()
  //   user3.id = 3
  //   user3.username = 'Terrence'
  //   mockAxios.mockResponse(rs([{user: user1, id: 1}, {user: user2, id: 2}]))
  //   await flushPromises()
  //   const vm = wrapper.vm as any
  //   expect(vm.$refs.manager.filter(user1, 'Fox', user1.username)).toBe(false)
  //   expect(vm.$refs.manager.filter(user3, 'Ter', user3.username)).toBe(true)
  //   expect(vm.$refs.manager.filter(user2, 'Bob', user2.username)).toBe(false)
  //   expect(vm.$refs.manager.filter(user3, '', user3.username)).toBe(false)
  // })
  // test('Auto-submits when the bound field is updated.', async() => {
  //   wrapper = mount(DummyRelated, vueSetup({
  //     store,
  //     stubs: ['router-link'],
  //   }))
  //   expect(mockAxios.request).toHaveBeenCalledWith(
  //     rq('/endpoint/', 'get', undefined, {signal: expect.any(Object)}),
  //   )
  //   mockAxios.reset()
  //   const vm = wrapper.vm as any
  //   vm.userForm.fields.user_id.update(3)
  //   await vm.$nextTick()
  //   expect(mockAxios.request).toHaveBeenCalledWith(
  //     rq('/endpoint/', 'post', {user_id: 3}, {}),
  //   )
  //   const user = genUser()
  //   user.id = 3
  //   const relation = {user, id: 4}
  //   mockAxios.mockResponse(rs(relation))
  //   await flushPromises()
  //   expect(vm.demoList.list[0].x).toEqual(relation)
  // })
})
