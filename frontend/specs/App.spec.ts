import mockAxios from './helpers/mock-axios'
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, shallowMount} from '@vue/test-utils'
import App from '../App.vue'
import {ArtStore, createStore} from '../store'
import flushPromises from 'flush-promises'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {userResponse} from './helpers/fixtures'
import {FormController} from '@/store/forms/form-controller'
import {dialogExpects, genAnon, rq, rs, vuetifySetup} from './helpers'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

jest.useFakeTimers()
// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
localVue.use(FormControllers)

describe('App.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
    mockAxios.reset()
    vuetifySetup()
    formRegistry.reset()
    singleRegistry.reset()
    profileRegistry.reset()
  })
  it('Fetches the user upon creation', async() => {
    const wrapper = shallowMount(App, {
      store,
      localVue,
      stubs: ['router-link', 'router-view'],
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      sync: false,
    })
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    const viewer = (wrapper.vm as any).viewer
    expect(viewer).toBeTruthy()
    expect(viewer.username).toBe('Fox')
  })
  it('Shows an error message if the user doesn\'t load.', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
      sync: false,
    })
    mockAxios.mockError!({
      response: {status: 500, request: {url: 'thing'}},
    })
    await flushPromises()
    const state = wrapper.vm.$store.state
    expect(state.errors.code).toBe(500)
    expect(
      wrapper.find('.error-container img').attributes().src).toBe('/static/images/500.png'
    )
  })
  it('Submits the support request form', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    const state = wrapper.vm.$store.state
    expect(state.showSupport).toBe(false)
    expect((wrapper.vm as any).showTicketSuccess).toBe(false)
    mockAxios.mockResponse(userResponse())
    const supportForm: FormController = (wrapper.vm as any).supportForm
    await flushPromises()
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
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
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
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
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
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    const supportForm = (wrapper.vm as any).supportForm
    expect(supportForm.fields.referring_url.value).toBe('/')
    wrapper.vm.$route.fullPath = '/test/'
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.referring_url.value).toBe('/test/')
  })
  it('Shows an alert', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#alert-bar').exists()).toBe(true)
  })
  it('Removes an alert automatically', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    await jest.runOnlyPendingTimers()
    expect(wrapper.find('#alert-bar').exists()).toBe(false)
    expect((wrapper.vm as any).alertDismissed).toBe(true)
  })
  it('Resets the alert dismissal value after the alert has cleared.', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    await jest.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  it('Manually resets alert dismissal, if needed', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    });
    (wrapper.vm as any).alertDismissed = true;
    (wrapper.vm as any).showAlert = true
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  it('Loads up search form data', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {q: 'Stuff', featured: 'true'}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
    })
    const vm = wrapper.vm as any
    expect(vm.searchForm.fields.q.value).toBe('Stuff')
  })
  it('Shows the markdown help section', async() => {
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
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
    const wrapper = mount(App, {
      store,
      localVue,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      sync: false,
      attachToDocument: true,
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
})
