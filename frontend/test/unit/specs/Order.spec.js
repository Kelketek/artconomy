import Order from '@/components/Order'
import { mount, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import VueRouter from 'vue-router'
import { router } from '../../../src/router'
import { UserHandler } from '../../../src/plugins/user'

let server, localVue

function genOrder () {
  return {
    'id': 1,
    'created_on': '2017-12-28T21:56:03.560910Z',
    'status': 8,
    'price': 3.0,
    'product': {
      'id': 2,
      'name': 'Test Product',
      'description': 'sxdbsdfgb',
      'category': 0,
      'revisions': 1,
      'hidden': false,
      'max_parallel': 0,
      'task_weight': 1,
      'expected_turnaround': 3,
      'user': {
        'id': 1,
        'username': 'Fox',
        'avatar_url': '/media/avatars/fox%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
      },
      'file': {
        'thumbnail': 'https://artconomy.vulpinity.com/media/art/2017/12/26/0c1915bc-b401-40c3-b77b-9afb9a1e5363.png.300x300_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2017/12/26/0c1915bc-b401-40c3-b77b-9afb9a1e5363.png.80x80_q85.jpg',
        'preview': 'https://artconomy.vulpinity.com/media/art/2017/12/26/0c1915bc-b401-40c3-b77b-9afb9a1e5363.png.500x500_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2017/12/26/0c1915bc-b401-40c3-b77b-9afb9a1e5363.png'
      },
      'rating': 2,
      'price': '3.00'
    },
    'details': 'Make Kai give Terry paw rubs!',
    'seller': {
      'id': 1,
      'username': 'Fox',
      'avatar_url': '/media/avatars/fox%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
    },
    'buyer': {
      'id': 1,
      'username': 'Fox',
      'avatar_url': '/media/avatars/fox%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
    },
    'adjustment': '12.00',
    'characters': [
      {
        'id': 3,
        'name': 'Kai',
        'description': '',
        'private': true,
        'open_requests': true,
        'open_requests_restrictions': '',
        'user': {
          'id': 1,
          'username': 'Fox',
          'avatar_url': '/media/avatars/fox%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
        },
        'primary_asset': null,
        'species': '',
        'gender': ''
      },
      {
        'id': 5,
        'name': 'Terrence',
        'description': '',
        'private': false,
        'open_requests': true,
        'open_requests_restrictions': '',
        'user': {
          'id': 3,
          'username': 'Foxie',
          'avatar_url': 'https://www.gravatar.com/avatar/95cbb0e4d2935fedbe8ed95e8b7fd3f7/?s=80'
        },
        'primary_asset': {
          'id': 19,
          'title': 'Terrence Doing someone',
          'caption': 'Breeding',
          'rating': 2,
          'file': {
            'notification': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.80x80_q85.jpg',
            'thumbnail': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.300x300_q85_crop-%2C0.jpg',
            'gallery': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.1000x700_q85.jpg',
            'full': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg'
          },
          'private': false,
          'created_on': '2017-12-25T02:50:31.800125Z',
          'uploaded_by': {
            'id': 3,
            'username': 'Foxie',
            'avatar_url': 'https://www.gravatar.com/avatar/95cbb0e4d2935fedbe8ed95e8b7fd3f7/?s=80'
          },
          'comment_count': 2,
          'favorite_count': 0,
          'comments_disabled': false
        },
        'species': '',
        'gender': ''
      }
    ],
    'stream_link': 'http://whatever.com/',
    'revisions': 3,
    'outputs': [
      {
        'id': 29,
        'title': 'Stuff her gooood!',
        'caption': 'Hell yeah!',
        'rating': 2,
        'file': {
          'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.80x80_q85.jpg',
          'thumbnail': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.300x300_q85_crop-%2C0.jpg',
          'gallery': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.1000x700_q85.jpg',
          'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg'
        },
        'private': false,
        'created_on': '2018-01-02T22:46:06.813423Z',
        'uploaded_by': {
          'id': 1,
          'username': 'Fox',
          'avatar_url': '/media/avatars/fox%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
        },
        'comment_count': 2,
        'favorite_count': 0,
        'comments_disabled': false
      }
    ]
  }
}

describe('Order.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
    localVue.use(VueRouter)
    localVue.use(UserHandler)
  })
  afterEach(function () {
    server.restore()
  })
  it('Grabs and populates the initial order data and renders it.', async() => {
    router.replace({name: 'Order', params: {username: 'testusername', orderID: 4}})
    let wrapper = mount(Order, {
      localVue,
      router,
      propsData: {
        username: 'testusername',
        orderID: 4
      }
    })
    wrapper.vm.$forceUser({username: 'testusername'})
    expect(server.requests.length).to.equal(3)
    let orderReq = server.requests[1]
    let revisionsReq = server.requests[2]
    expect(orderReq.url).to.equal('/api/sales/v1/order/4/')
    expect(orderReq.method).to.equal('GET')
    orderReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify(
        genOrder()
      )
    )
    expect(revisionsReq.url).to.equal('/api/sales/v1/order/4/revisions/')
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  })
})
