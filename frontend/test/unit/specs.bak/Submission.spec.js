import Submission from '@/components/Submission'
import { mount, createLocalVue } from '@vue/test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import VueRouter from 'vue-router'
import { router } from '../../../src/router/index'
import Vuetify from 'vuetify'
import { UserHandler } from '../../../src/plugins/user'
import {installFields} from '../helpers'
import VueFormGenerator from 'vue-form-generator'

let server, localVue

describe('Submission.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
    localVue.use(VueRouter)
    localVue.use(VueFormGenerator)
    localVue.use(UserHandler)
    localVue.use(Vuetify)
    installFields(localVue)
  })
  afterEach(function () {
    server.restore()
  })
  it('Grabs and populates the initial submission data and renders it.', async() => {
    router.replace({name: 'Submission', params: {'assetID': 1}})
    let wrapper = mount(Submission, {
      localVue,
      router
    })
    wrapper.vm.$forceUser({username: 'testusername'})
    expect(server.requests.length).to.equal(1)
    let subReq = server.requests[0]
    expect(subReq.url).to.equal('/api/profiles/v1/asset/1/')
    expect(subReq.method).to.equal('GET')
    subReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify(
        {
          title: 'Test Submission',
          caption: 'A very **testy** submission',
          owner: {
            id: 1,
            username: 'testusername'
          },
          file: {
            gallery: '/test_asset1.gallery.jpg',
            thumbnail: '/test_asset1.thumbnail.jpg',
            full: '/test_asset1.jpg'
          },
          artists: [],
          characters: []
        }
      )
    )
    await localVue.nextTick()
    expect(wrapper.find('.submission-description').text()).to.equal('A very testy submission')
  })
})
