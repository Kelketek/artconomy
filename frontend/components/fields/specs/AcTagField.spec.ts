import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuex from 'vuex'
import {flushPromises, rs, vuetifySetup} from '@/specs/helpers'
import Vuetify from 'vuetify'
import AcTagField from '@/components/fields/AcTagField.vue'
import mockAxios from '@/__mocks__/axios'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
jest.useFakeTimers()
let wrapper: Wrapper<Vue>

describe('ac-tag-field', () => {
  beforeEach(() => {
    vuetifySetup()
    mockAxios.reset()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Searches for tags', async() => {
    const tagList: string[] = []
    wrapper = mount(AcTagField, {localVue, propsData: {value: tagList}})
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
    wrapper = mount(AcTagField, {localVue, propsData: {value: tagList}})
    wrapper.find('input').setValue('Test')
    await jest.runAllTimers()
    mockAxios.mockResponse(rs(['Test', 'Test1', 'Test2']))
    await flushPromises()
  })
  it('Sets a tag and resets upon adding a space.', async() => {
    const tagList: string[] = []
    wrapper = mount(
      AcTagField, {localVue, propsData: {value: tagList}, sync: false, attachToDocument: true}
    )
    wrapper.find('input').setValue('Test ')
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).tags).toEqual(['Test'])
    expect((wrapper.vm as any).queryStore).toBe('')
  })
})
