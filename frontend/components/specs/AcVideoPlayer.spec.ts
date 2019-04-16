import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {vuetifySetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcVideoPlayer from '@/components/AcVideoPlayer.vue'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Profiles)
let wrapper: Wrapper<Vue>

const mockError = jest.spyOn(console, 'error')

describe('AcVideoPlayer.vue', () => {
  beforeEach(() => {
    vuetifySetup()
    mockError.mockClear()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Loads and types an audio file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    wrapper = mount(AcVideoPlayer, {localVue, propsData: {asset: submission}})
  })
})
