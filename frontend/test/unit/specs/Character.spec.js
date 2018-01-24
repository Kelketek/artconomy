import Character from '@/components/Character'
import { mount, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'

let server, localVue

describe('Character.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.$setUser = function () {}
    localVue.prototype.md = MarkDownIt()
  })
  afterEach(function () {
    server.restore()
  })
  it('Grabs and populates the initial character data and renders it.', async() => {
    let wrapper = mount(Character, {
      localVue,
      stubs: ['router-link', 'router-view'],
      mocks: {
        $route: {
          params: {character: 'testcharacter', username: 'testusername'},
          query: {}
        }
      },
      propsData: {
        username: 'testusername', characterName: 'testcharacter'
      }
    })
    expect(server.requests.length).to.equal(2)
    let charReq = server.requests[0]
    let assetReq = server.requests[1]
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
