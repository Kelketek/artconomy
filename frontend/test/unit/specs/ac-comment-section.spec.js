import AcCommentSection from '@/components/ac-comment-section'
import { mount, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import { checkJson } from '../helpers'

let server, localVue

let commentData = {
  'count': 5,
  'links': {
    'next': null,
    'previous': null
  },
  'size': 50,
  'results': [
    {
      'id': 2,
      'text': 'Why you so broken, commentses?',
      'created_on': '2017-12-18T17:13:34.579957Z',
      'edited_on': '2017-12-18T17:13:34.579981Z',
      'user': {
        'id': 2,
        'username': 'JimBob'
      },
      'children': [],
      'edited': false,
      'deleted': false
    },
    {
      'id': 3,
      'text': 'Yeah, why you suck?',
      'created_on': '2017-12-18T17:14:36.548188Z',
      'edited_on': '2017-12-18T17:14:36.548210Z',
      'user': {
        'id': 1,
        'username': 'Kelketek'
      },
      'children': [],
      'edited': false,
      'deleted': false
    },
    {
      'id': 4,
      'text': 'Additional commenting!',
      'created_on': '2017-12-18T17:22:28.682996Z',
      'edited_on': '2017-12-18T17:22:28.683020Z',
      'user': {
        'id': 1,
        'username': 'Kelketek'
      },
      'children': [],
      'edited': false,
      'deleted': false
    },
    {
      'id': 5,
      'text': 'Dis is a comment.',
      'created_on': '2017-12-18T17:36:08.328381Z',
      'edited_on': '2017-12-18T17:36:08.328406Z',
      'user': {
        'id': 1,
        'username': 'Kelketek'
      },
      'children': [
        {
          'id': 6,
          'text': 'This is a reply.',
          'created_on': '2017-12-18T17:40:14.997580Z',
          'edited_on': '2017-12-18T17:40:14.997620Z',
          'user': {
            'id': 1,
            'username': 'Kelketek'
          },
          'children': [],
          'edited': false,
          'deleted': false
        },
        {
          'id': 8,
          'text': 'This is another comment.',
          'created_on': '2017-12-18T18:25:38.180107Z',
          'edited_on': '2017-12-18T18:25:38.180219Z',
          'user': {
            'id': 1,
            'username': 'Kelketek'
          },
          'children': [],
          'edited': false,
          'deleted': false
        }
      ],
      'edited': false,
      'deleted': false
    },
    {
      'id': 9,
      'text': 'Here\'s another comment.',
      'created_on': '2017-12-18T18:25:51.880606Z',
      'edited_on': '2017-12-18T18:25:51.880643Z',
      'user': {
        'id': 1,
        'username': 'Kelketek'
      },
      'children': [],
      'edited': false,
      'deleted': false
    }
  ]
}

describe('ac-comment-section.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.$setUser = function () {}
    localVue.prototype.md = MarkDownIt()
    localVue.prototype.user = {
      username: 'Kelketek',
      id: 1
    }
  })
  afterEach(function () {
    server.restore()
  })
  it('Grabs and populates the initial character data and renders it.', async () => {
    let wrapper = mount(AcCommentSection, {
      localVue,
      stubs: ['router-link', 'router-view'],
      propsData: {
        commenturl: '/test/comments/',
        nesting: true,
        locked: false
      },
      mocks: {
        $route: {
          query: {}
        }
      }
    })
    expect(server.requests.length).to.equal(1)
    let commentReq = server.requests[0]
    expect(commentReq.url).to.equal('/test/comments/')
    commentReq.respond(
      200,
      {'Content-Type': 'application/json'},
      JSON.stringify(commentData)
    )
    await localVue.nextTick()
    // Must include new comment field.
    expect(wrapper.findAll('.comment-block').length).to.equal(8)
    expect(wrapper.find('.new-comment-block').exists()).to.equal(true)
    expect(wrapper.findAll('.fa-edit').length).to.equal(6)
    expect(wrapper.findAll('.fa-reply').length).to.equal(5)
  })
  it('Does not show a new/edit capabilitiees if comments are disabled.', async () => {
    let wrapper = mount(AcCommentSection, {
      localVue,
      stubs: ['router-link', 'router-view'],
      propsData: {
        commenturl: '/test/comments/',
        nesting: true,
        locked: true
      },
      mocks: {
        $route: {
          query: {}
        }
      }
    })
    expect(server.requests.length).to.equal(1)
    let commentReq = server.requests[0]
    expect(commentReq.url).to.equal('/test/comments/')
    commentReq.respond(
      200,
      {'Content-Type': 'application/json'},
      JSON.stringify(commentData)
    )
    await localVue.nextTick()
    // Must include new comment field.
    expect(wrapper.findAll('.comment-block').length).to.equal(7)
    expect(wrapper.find('.new-comment-block').exists()).to.equal(false)
    expect(wrapper.findAll('.fa-edit').length).to.equal(0)
    expect(wrapper.findAll('.fa-reply').length).to.equal(0)
  })
  it('Adds a new root-level comment', async () => {
    let wrapper = mount(AcCommentSection, {
      localVue,
      stubs: ['router-link', 'router-view'],
      propsData: {
        commenturl: '/test/comments/',
        nesting: true,
        locked: false
      },
      mocks: {
        $route: {
          query: {}
        }
      }
    })
    expect(server.requests.length).to.equal(1)
    let commentReq = server.requests[0]
    expect(commentReq.url).to.equal('/test/comments/')
    commentReq.respond(
      200,
      {'Content-Type': 'application/json'},
      JSON.stringify(commentData)
    )
    await localVue.nextTick()
    expect(wrapper.find('.new-comment-field').exists()).to.equal(false)
    wrapper.find('.new-comment-button').trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('.new-comment-field').exists()).to.equal(true)
    let saveButton = wrapper.find('.new-comment-block').find('.fa-save')
    expect(saveButton.exists())
    wrapper.vm.$refs.newComment.draft = 'This is a test comment'
    saveButton.trigger('click')
    expect(server.requests.length).to.equal(2)
    let newComment = server.requests[1]
    checkJson(
      newComment, {
        'data': {
          'text': 'This is a test comment'
        },
        'url': '/test/comments/',
        'method': 'POST'
      })
    newComment.respond(
      201,
      {'Content-Type': 'application/json'},
      JSON.stringify(
        {
          'id': 11,
          'text': 'This is a test comment',
          'created_on': '2017-12-18T18:25:51.880606Z',
          'edited_on': '2017-12-18T18:25:51.880643Z',
          'user': {
            'id': 1,
            'username': 'Kelketek'
          },
          'children': [],
          'edited': false,
          'deleted': false
        }
      )
    )
    await localVue.nextTick()
    expect(wrapper.findAll('.comment-block').length).to.equal(9)
    expect(wrapper.find('.new-comment-block').exists()).to.equal(true)
    expect(wrapper.findAll('.fa-edit').length).to.equal(7)
    expect(wrapper.findAll('.fa-reply').length).to.equal(6)
  })
})
