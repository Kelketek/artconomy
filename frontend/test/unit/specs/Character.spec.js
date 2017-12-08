import Character from '@/components/Character'
import { shallow, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'

let server, localVue

describe('Character.vue', () => {
  before(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.setUser = function () {}
    localVue.prototype.md = MarkDownIt()
  })
  after(function () {
    server.restore()
  })
  it('Grabs and populates the initial character data and renders it.', async() => {
    let wrapper = shallow(Character, {
      localVue,
      stubs: ['router-link', 'router-view'],
      mocks: {
        $route: {
          params: {character: 'testcharacter', username: 'testusername'},
          query: {}
        }
      }
    })
    expect(server.requests.length).to.equal(2)
    let charReq = server.requests[0]
    let assetReq = server.requests[1]
    expect(charReq.url).to.equal('/api/profiles/v1/testusername/characters/testcharacter/')
    expect(charReq.method).to.equal('GET')
    expect(assetReq.url).to.equal('/api/profiles/v1/testusername/characters/testcharacter/assets/')
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
          }
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
    let result = await localVue.nextTick()
    console.log(result)
    expect(wrapper.find('.character-description').html()).to.equal(
      '<div class="card-block character-description"><p>A very <strong>testy</strong> character</p>\n</div>')
    expect(wrapper.find('.character-panel-preview img').element.getAttribute('src')).to.equal('/test_asset1.jpg')
  })
})
