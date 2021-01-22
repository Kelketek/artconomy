import mockAxios from './helpers/mock-axios'
import Vue from 'vue'
import {mount, shallowMount, Wrapper} from '@vue/test-utils'
import App from '../App.vue'
import {ArtStore, createStore} from '../store'
import flushPromises from 'flush-promises'
import {userResponse} from './helpers/fixtures'
import {FormController} from '@/store/forms/form-controller'
import {cleanUp, createVuetify, dialogExpects, docTarget, genAnon, rq, rs, vueSetup} from './helpers'
import Vuetify from 'vuetify/lib'
import {createPinterestQueue} from '@/lib/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

window.pintrk = createPinterestQueue()
// @ts-ignore
window.__COMMIT_HASH__ = 'bogusHash'

describe('App.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Fetches the user upon creation', async() => {
    wrapper = shallowMount(App, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link', 'router-view'],
      mocks: {
        $route: {fullPath: '/', params: {}, query: {}},
      },
    })
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    const viewer = (wrapper.vm as any).viewer
    expect(viewer).toBeTruthy()
    expect(viewer.username).toBe('Fox')
  })
  it('Shows an error message if the user doesn\'t load.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
    })
    mockAxios.mockError!({
      response: {status: 500, request: {url: 'thing'}},
    })
    await flushPromises()
    const state = wrapper.vm.$store.state
    expect(state.errors.code).toBe(500)
    expect(
      wrapper.find('.error-container img').attributes().src).toBe('/static/images/500.png',
    )
  })
  it('Detects when a full interface should not be used due to a specific name', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/order/', name: 'NewOrder', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
    })
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(false)
  })
  it('Detects when a full interface should not be used due to a landing page', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/order/', name: 'LandingStuff', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],

    })
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(false)
  })
  it('Detects when a full interface should be used', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/order/', name: 'Thingsf', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],

    })
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(true)
  })
  it('Detects when a full interface should be used on a broken route', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/order/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],

    })
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(true)
  })
  it('Submits the support request form', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const state = wrapper.vm.$store.state
    expect(state.showSupport).toBe(false)
    const vm = wrapper.vm as any
    expect(vm.showTicketSuccess).toBe(false)
    mockAxios.mockResponse(userResponse())
    const supportForm: FormController = (wrapper.vm as any).supportForm
    await flushPromises()
    vm.setSupport(true)
    await vm.$nextTick()
    supportForm.fields.body.update('This is a test.')
    const submit = dialogExpects({wrapper, formName: 'supportRequest', fields: ['email', 'body']})
    submit.trigger('click')
    const response = rq('/api/lib/v1/support/request/', 'post',
      {
        email: 'fox@artconomy.com',
        body: 'This is a test.',
        referring_url: '/',
      }, {})
    expect(mockAxios.post).toHaveBeenCalledWith(...response)
    mockAxios.mockResponse(rs(undefined, {status: 204}))
    await flushPromises()
    expect(state.showSupport).toBe(false)
    expect((wrapper.vm as any).showTicketSuccess).toBe(true)
    const success = wrapper.find('#supportSuccess')
    expect(success.exists()).toBeTruthy()
    success.find('button').trigger('click')
    expect((wrapper.vm as any).showTicketSuccess).toBe(false)
  })
  it('Updates the email field when the viewer\'s email is updated.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const supportForm = (wrapper.vm as any).supportForm
    expect(supportForm.fields.email.value).toBe('')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(supportForm.fields.email.value).toBe('fox@artconomy.com')
    const editedUser = userResponse()
    editedUser.data.email = 'test@example.com';
    (wrapper.vm as any).viewerHandler.user.setX(editedUser.data)
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('test@example.com')
    ;(wrapper.vm as any).viewerHandler.user.setX(genAnon())
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('')
  })
  it('Updates the email field when the viewer\'s guest email is updated.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const supportForm = (wrapper.vm as any).supportForm
    expect(supportForm.fields.email.value).toBe('')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(supportForm.fields.email.value).toBe('fox@artconomy.com')
    const editedUser = userResponse()
    editedUser.data.email = 'test@example.com'
    editedUser.data.guest_email = 'test2@example.com'
    ;(wrapper.vm as any).viewerHandler.user.setX(editedUser.data)
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('test2@example.com')
    ;(wrapper.vm as any).viewerHandler.user.setX(genAnon())
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('')
  })
  it('Updates the referring_url field when the route has changed.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const supportForm = (wrapper.vm as any).supportForm
    expect(supportForm.fields.referring_url.value).toBe('/')
    wrapper.vm.$route.fullPath = '/test/'
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.referring_url.value).toBe('/test/')
  })
  it('Shows an alert', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#alert-bar').exists()).toBe(true)
  })
  it('Removes an alert automatically', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    await jest.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#alert-bar').exists()).toBe(false)
    expect((wrapper.vm as any).showAlert).toBe(false)
  })
  it('Resets the alert dismissal value after the alert has cleared.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    await jest.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  it('Manually resets alert dismissal, if needed', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    });
    (wrapper.vm as any).alertDismissed = true;
    (wrapper.vm as any).showAlert = true
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  it('Loads up search form data', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {q: 'Stuff', featured: 'true'}, name: null}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const vm = wrapper.vm as any
    vm.$route.name = 'Home'
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe('Stuff')
  })
  it('Shows the markdown help section', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.find('.markdown-rendered-help').exists()).toBe(false)
    vm.showMarkdownHelp = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.markdown-rendered-help').exists()).toBe(true)
    expect(store.state.markdownHelp).toBe(true)
    wrapper.find('#close-markdown-help').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.find('.markdown-rendered-help').exists()).toBe(true)
  })
  it('Changes the route key', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.routeKey).toEqual('')
    Vue.set(vm.$route.params, 'username', 'Bob')
    expect(vm.routeKey).toEqual('username:Bob|')
    Vue.set(vm.$route.params, 'characterName', 'Dude')
    expect(vm.routeKey).toEqual('characterName:Dude|username:Bob|')
    Vue.set(vm.$route.params, 'submissionId', '555')
    expect(vm.routeKey).toEqual('characterName:Dude|submissionId:555|username:Bob|')
  })
  it('Determines whether or not we are in dev mode', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    expect(vm.mode()).toBe('test')
    expect(vm.devMode).toBe(false)
    const mockMode = jest.spyOn(vm, 'mode')
    mockMode.mockImplementation(() => 'development')
    expect(vm.mode()).toBe('development')
    vm.forceRecompute += 1
    await vm.$nextTick()
    expect(vm.devMode).toBe(true)
  })
})
