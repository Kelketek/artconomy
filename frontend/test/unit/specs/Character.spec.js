import Character from '@/components/Character'
import { mount, createLocalVue } from '@vue/test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import VueRouter from 'vue-router'
import { router } from '../../../src/router/index'
import { UserHandler } from '../../../src/plugins/user'
import VueFormGenerator from 'vue-form-generator'
import { Shortcuts } from '../../../src/plugins/shortcuts'
import Vuetify from 'vuetify'

let server, localVue

describe('Character.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
    localVue.use(VueRouter)
    localVue.use(UserHandler)
    localVue.use(VueFormGenerator)
    localVue.use(Shortcuts)
    localVue.use(Vuetify)
  })
  afterEach(function () {
    server.restore()
  })
  it('Grabs and populates the initial character data and renders it.', async() => {
    // router.replace({name: 'Character', params: {username: 'testusername', characterName: 'testcharacter'}})
    let wrapper = mount(Character, {
      localVue,
      router,
      stubs: ['router-link', 'router-view'],
      propsData: {
        username: 'testusername', characterName: 'testcharacter'
      },
      mocks: {
        '$root.user': {username: 'Fox', rating: 3, sfw_mode: false}
      }
    })
    console.log('Viewer is:')
    console.log(wrapper.vm.viewer)
    wrapper.vm.$forceUser({username: 'Fox', rating: 3, sfw_mode: false})
    expect(server.requests.length).to.equal(3)
    let charReq = server.requests[1]
    let assetReq = server.requests[2]
    expect(charReq.url).to.equal('/api/profiles/v1/account/testusername/characters/testcharacter/')
    expect(charReq.method).to.equal('GET')
    expect(assetReq.url).to.equal('/api/profiles/v1/account/testusername/characters/testcharacter/assets/?size=4')
    expect(assetReq.method).to.equal('GET')
    charReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify(
        {
          name: 'testcharacter',
          description: 'A very **testy** character',
          user: {
            id: 1,
            username: 'testusername'
          },
          colors: [],
          primary_asset: {
            id: 1,
            file: '/test_asset1.jpg',
            title: 'Test asset 1',
            caption: 'Test caption 1',
            primary_asset: false,
            favorite_count: 3,
            comment_count: 2
          },
          tags: []
        }
      )
    )
    assetReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify(
        {
          page: 1,
          results: [
            {
              id: 1,
              file: '/test_asset1.jpg',
              title: 'Test asset 1',
              caption: 'Test caption 1',
              primary_asset: false,
              favorite_count: 3,
              comment_count: 2
            },
            {
              id: 2,
              file: '/test_asset2.jpg',
              title: 'Test asset 2',
              caption: 'Test caption 2',
              primary_asset: true,
              favorite_count: 5,
              comment_count: 8
            }
          ]
        }
      )
    )
    await localVue.nextTick()
    expect(wrapper.find('.character-description').text()).to.equal('A very testy character')
  })
})
