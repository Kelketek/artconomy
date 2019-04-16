import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, shallowMount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'
import {genAnon, makeSpace, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import mockAxios from '@/__mocks__/axios'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcGalleryPreview.vue', () => {
  beforeEach(() => {
    store = createStore()
    mockAxios.reset()
    profileRegistry.reset()
    singleRegistry.reset()
    vuetifySetup()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Displays a preview of a submission', () => {
    setViewer(store, genAnon())
    const submission = genSubmission()
    submission.id = 534
    wrapper = shallowMount(AcGalleryPreview, {
      localVue,
      store,
      propsData: {submission},
      sync: false,
      attachToDocument: true,
      stubs: ['router-link'],
    })
    const vm = wrapper.vm as any
    expect(vm.submissionLink).toEqual({name: 'Submission', params: {submissionId: 534}})
  })
})
