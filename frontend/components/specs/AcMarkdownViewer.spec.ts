import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {rq, rs, vuetifySetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcMarkdownViewer from '@/components/AcMarkdownViewer.vue'
import mockAxios from '@/__mocks__/axios'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Profiles)
let wrapper: Wrapper<Vue>

const mockError = jest.spyOn(console, 'error')

describe('AcMarkdownViewer.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    mockError.mockClear()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Loads and renders a markdown document', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/test.txt'}
    wrapper = mount(AcMarkdownViewer, {localVue, propsData: {asset: submission}})
    const vm = wrapper.vm as any
    expect(mockAxios.get).toHaveBeenCalledWith(...rq('https://example.com/test.txt', 'get', undefined, {}))
    mockAxios.mockResponse(rs('# Hello!'))
    expect(wrapper.find('h1').text()).toEqual('Hello!')
  })
})
