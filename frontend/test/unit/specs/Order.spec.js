import Order from '@/components/Order'
import { mount, createLocalVue } from '@vue/test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import VueRouter from 'vue-router'
import { router } from '../../../src/router'
import { UserHandler } from '../../../src/plugins/user'
import VueFormGenerator from 'vue-form-generator'
import BootstrapVue from 'bootstrap-vue'
import { Shortcuts } from '../../../src/plugins/shortcuts'
import { installFields } from '../helpers'
import Vuetify from 'vuetify'

let server, localVue

function genRevisions () {
  return [
    {
      'id': 6,
      'rating': 0,
      'file': {
        'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg.500x500_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg.80x80_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg'
      },
      'created_on': '2018-01-02T20:49:30.777699Z',
      'owner': 'Fox',
      'order': 1
    },
    {
      'id': 7,
      'rating': 2,
      'file': {
        'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg.500x500_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg.80x80_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg'
      },
      'created_on': '2018-01-02T20:49:40.521880Z',
      'owner': 'Fox',
      'order': 1
    },
    {
      'id': 8,
      'rating': 0,
      'file': {
        'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png.500x500_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png.80x80_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png'
      },
      'created_on': '2018-01-02T20:49:47.771963Z',
      'owner': 'Fox',
      'order': 1
    },
    {
      'id': 11,
      'rating': 2,
      'file': {
        'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg.500x500_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg.80x80_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg'
      },
      'created_on': '2018-01-02T21:18:48.284490Z',
      'owner': 'Fox',
      'order': 1
    }
  ]
}

function genOrder () {
  return {
    'id': 1,
    'created_on': '2017-12-28T21:56:03.560910Z',
    'status': 1,
    'price': 3.0,
    'private': false,
    'product': {
      'id': 2,
      'name': 'Test Product',
      'description': 'sxdbsdfgb',
      'category': 0,
      'revisions': 1,
      'hidden': false,
      'max_parallel': 0,
      'task_weight': 1,
      'tags': [],
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
      'username': 'Cat',
      'avatar_url': '/media/avatars/cat%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
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
          'username': 'Cat',
          'avatar_url': '/media/avatars/cat%40vulpinity.com/resized/80/41b0fbde-0fbc-409f-b848-57ac4db98957.png'
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
          'tags': ['fox'],
          'file': {
            'notification': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.80x80_q85.jpg',
            'thumbnail': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.300x300_q85_crop-%2C0.jpg',
            'gallery': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg.1000x700_q85.jpg',
            'full': 'https://artconomy.vulpinity.com/media/art/2017/12/25/1e725d30-a873-42b8-9267-a9ce73a5d6ff.jpeg'
          },
          'private': false,
          'created_on': '2017-12-25T02:50:31.800125Z',
          'owner': {
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
        'tags': [],
        'rating': 2,
        'file': {
          'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.80x80_q85.jpg',
          'thumbnail': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.300x300_q85_crop-%2C0.jpg',
          'gallery': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg.1000x700_q85.jpg',
          'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd_RtuACZj.jpeg'
        },
        'private': false,
        'created_on': '2018-01-02T22:46:06.813423Z',
        'owner': {
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
    localVue.use(BootstrapVue)
    localVue.use(VueFormGenerator)
    localVue.use(Shortcuts)
    localVue.use(Vuetify)
    installFields(localVue)
  })
  afterEach(function () {
    server.restore()
  })

  function sellerBootstrap (order, revisions) {
    router.replace({name: 'Order', params: {username: 'Fox', orderID: 4}})
    let wrapper = mount(Order, {
      localVue,
      router,
      propsData: {
        username: 'Fox',
        orderID: 4
      }
    })
    wrapper.vm.$forceUser({username: 'Fox', fee: 0.01, blacklist: []})
    if (order) {
      let orderReq = server.requests[1]
      orderReq.respond(
        200,
        { 'Content-Type': 'application/json' },
        JSON.stringify(
          order
        )
      )
    }
    if (revisions) {
      let revisionsReq = server.requests[2]
      revisionsReq.respond(
        200,
        { 'Content-Type': 'application/json' },
        JSON.stringify({results: revisions})
      )
    }
    return wrapper
  }
  function buyerBootstrap (order, revisions) {
    router.replace({name: 'Order', params: {username: 'Cat', orderID: 4}})
    let wrapper = mount(Order, {
      localVue,
      router,
      propsData: {
        username: 'Cat',
        orderID: 4
      }
    })
    wrapper.vm.$forceUser({username: 'Cat', blacklist: []})
    if (order) {
      let orderReq = server.requests[1]
      orderReq.respond(
        200,
        { 'Content-Type': 'application/json' },
        JSON.stringify(
          order
        )
      )
    }
    if (revisions) {
      let revisionsReq = server.requests[2]
      revisionsReq.respond(
        200,
        { 'Content-Type': 'application/json' },
        JSON.stringify({results: revisions})
      )
    }
    return wrapper
  }

  it('Grabs and populates the initial order data and renders it for seller.', async() => {
    let wrapper = sellerBootstrap()
    expect(server.requests.length).to.equal(4)
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
    revisionsReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify([])
    )
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(true)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Grabs and populates the initial order data and renders it for the buyer.', async() => {
    let wrapper = buyerBootstrap()
    expect(server.requests.length).to.equal(4)
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
    revisionsReq.respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify({results: []})
    )
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Asks buyer for card info once an order is accepted.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 2
    let wrapper = buyerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(true)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Stands by for seller when an order is accepted.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 2
    let wrapper = sellerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Lets the seller know once it is paid.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 3
    let wrapper = sellerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(true)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Stands by for the buyer once it is queued.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 3
    let wrapper = buyerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Stands by for the buyer once it is in progress.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 4
    let wrapper = buyerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Gives upload interfaces to the seller once it is in progress.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 4
    let wrapper = sellerBootstrap(order, [])
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(true)
    expect(wrapper.find('#field-rating').exists()).to.equal(true)
    expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    expect(wrapper.find('.revision-upload').exists()).to.equal(true)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Shows revisions to the buyer when in progress.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 4
    let revisions = genRevisions()
    revisions.pop()
    let wrapper = buyerBootstrap(order, revisions)
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    expect(wrapper.findAll('.order-revision .fa-trash-o').length).to.equal(0)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Shows revisions to the seller when in progress.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 4
    let revisions = genRevisions()
    revisions.pop()
    let wrapper = sellerBootstrap(order, revisions)
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(true)
    expect(wrapper.find('#field-rating').exists()).to.equal(true)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(true)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    // Only the last one should show a delete button.
    expect(wrapper.findAll('.order-revision .fa-trash-o').length).to.equal(1)
    expect(wrapper.find('.final-preview').exists()).to.equal(false)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Shows the final to the buyer when in review.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 5
    let wrapper = buyerBootstrap(order, genRevisions())
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    expect(wrapper.find('.final-preview').exists()).to.equal(true)
    expect(wrapper.find('.dispute-button').exists()).to.equal(true)
    expect(wrapper.find('.approve-button').exists()).to.equal(true)
  })
  it('Stands by for the seller when in review.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 5
    let wrapper = sellerBootstrap(order, genRevisions())
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    expect(wrapper.find('.final-preview').exists()).to.equal(true)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Stands by for the seller when in dispute.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 7
    let wrapper = sellerBootstrap(order, genRevisions())
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(true)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    expect(wrapper.find('.final-preview').exists()).to.equal(true)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  it('Stands by for the buyer when in dispute.', async() => {
    let order = genOrder()
    // Payment Pending
    order.status = 7
    let wrapper = buyerBootstrap(order, genRevisions())
    await localVue.nextTick()
    expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
    expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
    expect(wrapper.find('.pay-button').exists()).to.equal(false)
    expect(wrapper.find('.refund-button').exists()).to.equal(false)
    expect(wrapper.find('#field-rating').exists()).to.equal(false)
    expect(wrapper.find('.revisions-section').exists()).to.equal(true)
    expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    expect(wrapper.findAll('.order-revision').length).to.equal(3)
    expect(wrapper.find('.final-preview').exists()).to.equal(true)
    expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    expect(wrapper.find('.approve-button').exists()).to.equal(true)
  })
})
