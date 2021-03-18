import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, vueSetup, mount} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcAudioPlayer from '@/components/AcAudioPlayer.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcAudioPlayer.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads and types an audio file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    // @ts-ignore
    wrapper = mount(AcAudioPlayer, {localVue, propsData: {asset: submission}})
    const vm = wrapper.vm as any
    expect(vm.type).toBe('audio/mp3')
  })
})
