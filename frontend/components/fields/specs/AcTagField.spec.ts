import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {cleanUp, createVuetify, flushPromises, rs, vueSetup} from '@/specs/helpers'
import {Vuetify} from 'vuetify/types'
import AcTagField from '@/components/fields/AcTagField.vue'
import mockAxios from '@/__mocks__/axios'

const localVue = vueSetup()
jest.useFakeTimers()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('ac-tag-field', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Searches for tags', async() => {
    const tagList: string[] = []
    wrapper = mount(AcTagField, {
      localVue,
      vuetify,
      propsData: {value: tagList},
    })
    wrapper.find('input').setValue('Test')
    await jest.runAllTimers()
    expect(mockAxios.get).toHaveBeenCalledWith(
      '/api/profiles/v1/search/tag/',
      undefined,
      {cancelToken: {}, headers: {'Content-Type': 'application/json; charset=utf-8'}, params: {q: 'Test'}}
    )
  })
  it('Accepts a response from the server on its query', async() => {
    const tagList: string[] = []
    wrapper = mount(AcTagField, {
      localVue,
      vuetify,
      propsData: {value: tagList},
    })
    wrapper.find('input').setValue('Test')
    await jest.runAllTimers()
    mockAxios.mockResponse(rs(['Test', 'Test1', 'Test2']))
    await flushPromises()
  })
  it('Sets a tag and resets upon adding a space.', async() => {
    const tagList: string[] = []
    wrapper = mount(
      AcTagField, {
        localVue,
        vuetify,
        propsData: {value: tagList},
        sync: false,
        attachToDocument: true,
      })
    wrapper.find('input').setValue('Test ')
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
  it('Does not redundantly add a tag.', async() => {
    const tagList: string[] = ['Test']
    wrapper = mount(
      AcTagField, {
        localVue,
        vuetify,
        propsData: {value: tagList},
        sync: false,
        attachToDocument: true,
      })
    wrapper.find('input').setValue('Test ')
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
  it('Performs the string-value workaround for mobile Chrome 81.', async() => {
    const tagList: string[] = ['Test']
    wrapper = mount(
      AcTagField, {
        localVue,
        vuetify,
        propsData: {value: tagList},
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    vm.tags = 'Stuff'
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test', 'Stuff'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
  it('Reverts the tag list Chrome 81.', async() => {
    const tagList: string[] = ['Test']
    wrapper = mount(
      AcTagField, {
        localVue,
        vuetify,
        propsData: {value: tagList},
        sync: false,
        attachToDocument: true,
      })
    const vm = wrapper.vm as any
    vm.tags = ' ,'
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
})
