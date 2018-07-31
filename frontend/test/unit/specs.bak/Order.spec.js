import Order from '@/components/Order'
import {mount, createLocalVue} from '@vue/test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import VueRouter from 'vue-router'
import {router} from '../../../src/router/index'
import {UserHandler} from '../../../src/plugins/user'
import VueFormGenerator from 'vue-form-generator'
import {Shortcuts} from '../../../src/plugins/shortcuts'
import {installFields} from '../helpers'
import Vuetify from 'vuetify'

let server, localVue

// function genRevisions () {
//   return [
//     {
//       'id': 6,
//       'rating': 0,
//       'file': {
//         'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg.500x500_q85.jpg',
//         'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg.80x80_q85.jpg',
//         'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/edb1cd8e-e8b3-4ef5-afb2-69c16e69ff4b.jpeg'
//       },
//       'created_on': '2018-01-02T20:49:30.777699Z',
//       'owner': 'Fox',
//       'order': 1
//     },
//     {
//       'id': 7,
//       'rating': 2,
//       'file': {
//         'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg.500x500_q85.jpg',
//         'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg.80x80_q85.jpg',
//         'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/9aecfcc8-aa30-4cd1-aadb-5fdc20927ea2.jpeg'
//       },
//       'created_on': '2018-01-02T20:49:40.521880Z',
//       'owner': 'Fox',
//       'order': 1
//     },
//     {
//       'id': 8,
//       'rating': 0,
//       'file': {
//         'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png.500x500_q85.jpg',
//         'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png.80x80_q85.jpg',
//         'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/86ed4fcf-d0c1-4d54-aabb-711180037222.png'
//       },
//       'created_on': '2018-01-02T20:49:47.771963Z',
//       'owner': 'Fox',
//       'order': 1
//     },
//     {
//       'id': 11,
//       'rating': 2,
//       'file': {
//         'preview': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg.500x500_q85.jpg',
//         'notification': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg.80x80_q85.jpg',
//         'full': 'https://artconomy.vulpinity.com/media/art/2018/01/02/5fbd090a-af0c-42e4-ae7d-b584ef92e8dd.jpeg'
//       },
//       'created_on': '2018-01-02T21:18:48.284490Z',
//       'owner': 'Fox',
//       'order': 1
//     }
//   ]
// }

function genOrder () {
  return {
    'id': 1,
    'created_on': '2018-07-27T12:13:22.166445-05:00',
    'status': 8,
    'price': 50.0,
    'product': {
      'id': 1,
      'name': 'Refsheet',
      'description': 'Get a reference sheet of your character!',
      'revisions': 1,
      'hidden': false,
      'max_parallel': 0,
      'task_weight': 1,
      'expected_turnaround': '3.00',
      'user': {
        'id': 2,
        'username': 'Jerp',
        'avatar_url': 'https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0/?s=80',
        'biography': '',
        'has_products': true,
        'favorites_hidden': false,
        'watching': false,
        'blocked': false,
        'commission_info': '',
        'stars': null
      },
      'file': {
        'thumbnail': 'https://artconomy.vulpinity.com/media/art/2018/07/27/vulpyref.png.300x300_q85.png',
        'preview': 'https://artconomy.vulpinity.com/media/art/2018/07/27/vulpyref.png.500x500_q85.png',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/07/27/vulpyref.png.80x80_q85.png',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/07/27/vulpyref.png'
      },
      'rating': 0,
      'price': '50.00',
      'tags': ['ref', 'reference_sheet', 'refsheet', 'colored'],
      'preview': null
    },
    'details': 'Draw her wahing the joint up.',
    'seller': {
      'id': 2,
      'username': 'Jerp',
      'avatar_url': 'https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0/?s=80',
      'stars': null
    },
    'buyer': {
      'id': 1,
      'username': 'Fox',
      'avatar_url': 'https://www.gravatar.com/avatar/18884bee632aa98dcd30661cc7fb4822/?s=80',
      'stars': '5.00'
    },
    'adjustment': '0.00',
    'characters': [{
      'id': 1,
      'name': 'Kai',
      'description': '',
      'private': false,
      'open_requests': false,
      'open_requests_restrictions': '',
      'user': {
        'id': 1,
        'username': 'Fox',
        'avatar_url': 'https://www.gravatar.com/avatar/18884bee632aa98dcd30661cc7fb4822/?s=80',
        'stars': '5.00'
      },
      'primary_asset': {
        'id': 1,
        'title': 'Kai refsheet',
        'caption': 'She\'s bein\' a wah!',
        'rating': 1,
        'file': {
          'thumbnail': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.300x300_q85_crop-%2C0.jpg',
          'gallery': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.1000x700_q85.jpg',
          'notification': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.80x80_q85.jpg',
          'full': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png'
        },
        'private': false,
        'created_on': '2018-07-27T13:25:20.727746-05:00',
        'owner': {
          'id': 1,
          'username': 'Fox',
          'avatar_url': 'https://www.gravatar.com/avatar/18884bee632aa98dcd30661cc7fb4822/?s=80',
          'stars': '5.00'
        },
        'comment_count': 1,
        'favorite_count': 0,
        'comments_disabled': false,
        'tags': [],
        'subscribed': true,
        'preview': null
      },
      'tags': ['female', 'red_panda'],
      'colors': [],
      'taggable': true,
      'attributes': [{'id': 1, 'key': 'sex', 'value': 'Female', 'sticky': true}, {
        'id': 2,
        'key': 'species',
        'value': 'Red Panda',
        'sticky': true
      }],
      'transfer': null,
      'shared_with': [{
        'id': 2,
        'username': 'Jerp',
        'avatar_url': 'https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0/?s=80',
        'stars': null
      }]
    }],
    'stream_link': '',
    'revisions': 1,
    'outputs': [{
      'id': 1,
      'title': 'Kai refsheet',
      'caption': 'She\'s bein\' a wah!',
      'rating': 1,
      'file': {
        'thumbnail': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.300x300_q85_crop-%2C0.jpg',
        'gallery': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.1000x700_q85.jpg',
        'notification': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png.80x80_q85.jpg',
        'full': 'https://artconomy.vulpinity.com/media/art/2018/07/27/art/2018/07/27/kairef-color.png'
      },
      'private': false,
      'created_on': '2018-07-27T13:25:20.727746-05:00',
      'owner': {
        'id': 1,
        'username': 'Fox',
        'avatar_url': 'https://www.gravatar.com/avatar/18884bee632aa98dcd30661cc7fb4822/?s=80',
        'stars': '5.00'
      },
      'comment_count': 1,
      'favorite_count': 0,
      'comments_disabled': false,
      'tags': [],
      'subscribed': true,
      'preview': null
    }],
    'private': false,
    'subscribed': true,
    'adjustment_task_weight': 0,
    'adjustment_expected_turnaround': '0.00',
    'expected_turnaround': '6.00',
    'task_weight': 1,
    'paid_on': '2018-07-27T13:23:55.305995-05:00',
    'dispute_available_on': '2018-08-08',
    'auto_finalize_on': '2018-08-01',
    'started_on': '2018-07-27T13:24:08.565789-05:00'
  }
}

describe('Order.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
    localVue.use(VueRouter)
    localVue.use(UserHandler)
    localVue.use(VueFormGenerator)
    localVue.use(Shortcuts)
    localVue.use(Vuetify)
    installFields(localVue)
  })
  afterEach(function () {
    server.restore()
  })

  function sellerBootstrap (order, revisions) {
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
        {'Content-Type': 'application/json'},
        JSON.stringify(
          order
        )
      )
    }
    if (revisions) {
      let revisionsReq = server.requests[2]
      revisionsReq.respond(
        200,
        {'Content-Type': 'application/json'},
        JSON.stringify({results: revisions})
      )
    }
    return wrapper
  }

  // function buyerBootstrap (order, revisions) {
  //   router.replace({name: 'Order', params: {username: 'Cat', orderID: 4}})
  //   let wrapper = mount(Order, {
  //     localVue,
  //     router,
  //     propsData: {
  //       username: 'Cat',
  //       orderID: 4
  //     }
  //   })
  //   wrapper.vm.$forceUser({username: 'Cat', blacklist: []})
  //   if (order) {
  //     let orderReq = server.requests[1]
  //     orderReq.respond(
  //       200,
  //       { 'Content-Type': 'application/json' },
  //       JSON.stringify(
  //         order
  //       )
  //     )
  //   }
  //   if (revisions) {
  //     let revisionsReq = server.requests[2]
  //     revisionsReq.respond(
  //       200,
  //       { 'Content-Type': 'application/json' },
  //       JSON.stringify({results: revisions})
  //     )
  //   }
  //   return wrapper
  // }
  it('Grabs and populates the initial order data and renders it for seller.', async () => {
    let wrapper = sellerBootstrap()
    expect(server.requests.length).to.equal(5)
    let orderReq = server.requests[1]
    let revisionsReq = server.requests[2]
    expect(orderReq.url).to.equal('/api/sales/v1/order/4/')
    expect(orderReq.method).to.equal('GET')
    console.log('======HEY YOU!!!!=====')
    // orderReq.respond(
    //   200,
    //   {'Content-Type': 'application/json'},
    //   JSON.stringify(
    //     genOrder()
    //   )
    // )
    // expect(revisionsReq.url).to.equal('/api/sales/v1/order/4/revisions/')
    // revisionsReq.respond(
    //   200,
    //   { 'Content-Type': 'application/json' },
    //   JSON.stringify([])
    // )
    // await localVue.nextTick()
    // expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
    // expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
    // expect(wrapper.find('.accept-order-btn').exists()).to.equal(true)
    // expect(wrapper.find('.pay-button').exists()).to.equal(false)
    // expect(wrapper.find('.refund-button').exists()).to.equal(false)
    // expect(wrapper.find('#field-rating').exists()).to.equal(false)
    // expect(wrapper.find('.revisions-section').exists()).to.equal(false)
    // expect(wrapper.find('.revision-upload').exists()).to.equal(false)
    // expect(wrapper.find('.final-preview').exists()).to.equal(false)
    // expect(wrapper.find('.dispute-button').exists()).to.equal(false)
    // expect(wrapper.find('.approve-button').exists()).to.equal(false)
  })
  // it('Grabs and populates the initial order data and renders it for the buyer.', async() => {
  //   let wrapper = buyerBootstrap()
  //   expect(server.requests.length).to.equal(5)
  //   let orderReq = server.requests[1]
  //   let revisionsReq = server.requests[2]
  //   expect(orderReq.url).to.equal('/api/sales/v1/order/4/')
  //   expect(orderReq.method).to.equal('GET')
  //   orderReq.respond(
  //     200,
  //     { 'Content-Type': 'application/json' },
  //     JSON.stringify(
  //       genOrder()
  //     )
  //   )
  //   expect(revisionsReq.url).to.equal('/api/sales/v1/order/4/revisions/')
  //   revisionsReq.respond(
  //     200,
  //     { 'Content-Type': 'application/json' },
  //     JSON.stringify({results: []})
  //   )
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Asks buyer for card info once an order is accepted.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 2
  //   let wrapper = buyerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(true)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Stands by for seller when an order is accepted.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 2
  //   let wrapper = sellerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(true)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Lets the seller know once it is paid.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 3
  //   let wrapper = sellerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(true)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Stands by for the buyer once it is queued.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 3
  //   let wrapper = buyerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Stands by for the buyer once it is in progress.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 4
  //   let wrapper = buyerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Gives upload interfaces to the seller once it is in progress.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 4
  //   let wrapper = sellerBootstrap(order, [])
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(true)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(true)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(false)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(true)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Shows revisions to the buyer when in progress.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 4
  //   let revisions = genRevisions()
  //   revisions.pop()
  //   let wrapper = buyerBootstrap(order, revisions)
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   expect(wrapper.findAll('.order-revision .fa-trash-o').length).to.equal(0)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Shows revisions to the seller when in progress.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 4
  //   let revisions = genRevisions()
  //   revisions.pop()
  //   let wrapper = sellerBootstrap(order, revisions)
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(true)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(true)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(true)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   // Only the last one should show a delete button.
  //   expect(wrapper.findAll('.order-revision .fa-trash-o').length).to.equal(1)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(false)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Shows the final to the buyer when in review.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 5
  //   let wrapper = buyerBootstrap(order, genRevisions())
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(true)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(true)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(true)
  // })
  // it('Stands by for the seller when in review.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 5
  //   let wrapper = sellerBootstrap(order, genRevisions())
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(true)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Stands by for the seller when in dispute.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 7
  //   let wrapper = sellerBootstrap(order, genRevisions())
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(true)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(true)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(false)
  // })
  // it('Stands by for the buyer when in dispute.', async() => {
  //   let order = genOrder()
  //   // Payment Pending
  //   order.status = 7
  //   let wrapper = buyerBootstrap(order, genRevisions())
  //   await localVue.nextTick()
  //   expect(wrapper.find('.order-details').text()).to.equal('Make Kai give Terry paw rubs!')
  //   expect(wrapper.find('.cancel-order-button').exists()).to.equal(false)
  //   expect(wrapper.find('.accept-order-btn').exists()).to.equal(false)
  //   expect(wrapper.find('.pay-button').exists()).to.equal(false)
  //   expect(wrapper.find('.refund-button').exists()).to.equal(false)
  //   expect(wrapper.find('#field-rating').exists()).to.equal(false)
  //   expect(wrapper.find('.revisions-section').exists()).to.equal(true)
  //   expect(wrapper.find('.revision-upload').exists()).to.equal(false)
  //   expect(wrapper.findAll('.order-revision').length).to.equal(3)
  //   expect(wrapper.find('.final-preview').exists()).to.equal(true)
  //   expect(wrapper.find('.dispute-button').exists()).to.equal(false)
  //   expect(wrapper.find('.approve-button').exists()).to.equal(true)
  // })
})
