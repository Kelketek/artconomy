import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, vueSetup, mount} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcVideoPlayer from '@/components/AcVideoPlayer.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcVideoPlayer.vue', () => {
  beforeEach(() => {
    mockError.mockClear()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads and types an audio file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    wrapper = mount(AcVideoPlayer, {localVue, vuetify, propsData: {asset: submission}})
  })
})
