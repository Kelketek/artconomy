import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, docTarget, flushPromises, rq, rs, vueSetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcMarkdownViewer from '@/components/AcMarkdownViewer.vue'
import mockAxios from '@/__mocks__/axios'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcMarkdownViewer.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads and renders a markdown document', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/test.txt'}
    wrapper = mount(AcMarkdownViewer, {
      localVue,
      vuetify,
      propsData: {asset: submission},

      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('https://example.com/test.txt', 'get', undefined, {}))
    mockAxios.mockResponse(rs('# Hello!'))
    await flushPromises()
    expect(wrapper.find('h1').text()).toEqual('Hello!')
  })
})
