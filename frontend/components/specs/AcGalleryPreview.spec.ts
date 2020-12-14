import Vue from 'vue'
import {shallowMount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, genAnon, setViewer, vueSetup} from '@/specs/helpers'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcGalleryPreview.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Displays a preview of a submission', async() => {
    setViewer(store, genAnon())
    const submission = genSubmission()
    submission.id = 534
    wrapper = shallowMount(AcGalleryPreview, {
      localVue,
      store,
      vuetify,
      propsData: {submission},

      attachTo: docTarget(),
      stubs: ['router-link'],
    })
    const vm = wrapper.vm as any
    expect(vm.submissionLink).toEqual({name: 'Submission', params: {submissionId: 534}})
  })
})
