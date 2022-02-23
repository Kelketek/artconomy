import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, flushPromises, rs, vueSetup, vuetifySetup, mount, rq} from '@/specs/helpers'
import AcUserSelect from '@/components/fields/AcUserSelect.vue'
import mockAxios from '@/__mocks__/axios'
import {genUser} from '@/specs/helpers/fixtures'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
jest.useFakeTimers()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcUserSelect.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    jest.clearAllTimers()
    cleanUp(wrapper)
  })
  it('Searches for users', async() => {
    const tagList: number[] = []
    wrapper = mount(AcUserSelect, {
      localVue,
      vuetify,
      attachTo: docTarget(),
      propsData: {value: tagList},
    })
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalled()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/v1/search/user/',
      'get',
      undefined,
      {cancelToken: expect.any(Object), headers: {'Content-Type': 'application/json; charset=utf-8'}, params: {q: 'Test'}},
    ))
  })
  it('Searches for users with a tagging modifier', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {value: tagList, tagging: true},
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    expect(mockAxios.request).toHaveBeenCalled()
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/v1/search/user/',
      'get',
      undefined,
      {
        cancelToken: expect.any(Object),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        params: {q: 'Test', tagging: true},
      },
    ))
  })
  it('Accepts a response from the server on its query', async() => {
    const tagList: number[] = []
    wrapper = mount(AcUserSelect, {
      localVue,
      vuetify,
      attachTo: docTarget(),
      propsData: {value: tagList},
    })
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    mockAxios.mockResponse(rs({results: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}]}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).items).toEqual([{username: 'Test', id: 1}, {username: 'Test2', id: 2}])
  })
  it('Sets a tag and resets upon adding a space when mode is multiple.', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {value: tagList},
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    mockAxios.mockResponse(rs({results: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}]}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('input').setValue('Test ')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual([1])
    expect((wrapper.vm as any).query).toBe(null)
  })
  it('Sets a tag and resets upon adding a space when mode is not multiple.', async() => {
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {value: null, multiple: false},
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    mockAxios.mockResponse(rs({results: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}]}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('input').setValue('Test ')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(1)
    expect((wrapper.vm as any).query).toBe(null)
  })
  it('Does nothing to the query if adding a space with no results.', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {value: tagList},
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    mockAxios.mockResponse(rs({results: []}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    wrapper.find('input').setValue('Test ')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual([])
    expect((wrapper.vm as any).query).toBe('Test ')
  })
  it('Prepopulates with initial items', async() => {
    const tagList: number[] = []
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: tagList, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    expect((wrapper.vm as any).items).toEqual([{username: 'Test', id: 1}, {username: 'Test2', id: 2}])
  })
  it('Resets the query if adding an item', async() => {
    const tagList: number[] = [1]
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: tagList, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    wrapper.setProps({value: [1, 2]})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).query).toBe(null)
  })
  it('Does not reset the query if removing an item', async() => {
    const tagList: number[] = [1, 2]
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: tagList, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    wrapper.setProps({value: [1]})
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).query).toBe('Test')
  })
  it('Always returns false when filtering an empty string', async() => {
    const tagList: number[] = [1]
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: tagList, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    const vm = wrapper.vm as any
    const user = genUser()
    expect(vm.itemFilter(user, '', 'Fox')).toBe(false)
  })
  it('Returns false when already selected for the single item', async() => {
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: null, multiple: false, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    const vm = wrapper.vm as any
    const user = {username: 'Test', id: 1}
    expect(vm.itemFilter(user, 'Test', 'Test')).toBe(true)
    wrapper.setProps({
      value: 1, multiple: false, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
    })
    await wrapper.vm.$nextTick()
    expect(vm.itemFilter(user, 'Test', 'Test')).toBe(false)
  })
  it('Calls a custom filter', () => {
    const mockFilter = jest.fn()
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: 1,
          multiple: false,
          initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
          filter: mockFilter,
        },
      },
    )
    const vm = wrapper.vm as any
    const user = {username: 'Test', id: 1}
    vm.itemFilter(user, 'Test', 'Test')
    expect(mockFilter).toHaveBeenCalledWith(user, 'Test', 'Test')
  })
  it('Clears tags when upstream clears them', async() => {
    wrapper = mount(
      AcUserSelect, {
        localVue,
        vuetify,
        attachTo: docTarget(),
        propsData: {
          value: [1], initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
        },
      },
    )
    const vm = wrapper.vm as any
    expect(vm.tags).toEqual([1])
    wrapper.setProps({
      value: null, initItems: [{username: 'Test', id: 1}, {username: 'Test2', id: 2}],
    })
    await vm.$nextTick()
    expect(vm.tags).toEqual([])
  })
})
