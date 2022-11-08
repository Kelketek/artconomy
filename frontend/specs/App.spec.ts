import mockAxios from './helpers/mock-axios'
import Vue, {VueConstructor} from 'vue'
import {Wrapper} from '@vue/test-utils'
import App from '../App.vue'
import {ArtStore, createStore} from '@/store'
import flushPromises from 'flush-promises'
import {genUser} from './helpers/fixtures'
import {FormController} from '@/store/forms/form-controller'
import {cleanUp, createVuetify, dialogExpects, docTarget, genAnon, rq, rs, vueSetup, mount, setViewer} from './helpers'
import Vuetify from 'vuetify/lib'
import {WS} from 'jest-websocket-mock'
import {socketNameSpace} from '@/plugins/socket'

let localVue: VueConstructor
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

// @ts-ignore
window.__COMMIT_HASH__ = 'bogusHash'
socketNameSpace.socketClass = WebSocket

describe('App.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    localVue = vueSetup()
    store = createStore()
    vuetify = createVuetify()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
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
  it('Opens and closes an age verification dialog', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/order/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    store.commit('setShowAgeVerification', true)
    await vm.$nextTick()
    expect(store.state.showAgeVerification).toBe(true)
    expect(vm.prerendering).toBe(false)
    expect(vm.viewerHandler.user.x).toBeTruthy()
    wrapper.find('.dialog-closer').trigger('click')
    await vm.$nextTick()
    expect(wrapper.find('dialog-closer').exists()).toBe(false)
  })
  it('Submits the support request form', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const state = wrapper.vm.$store.state
    expect(state.showSupport).toBe(false)
    const vm = wrapper.vm as any
    expect(vm.showTicketSuccess).toBe(false)
    const supportForm: FormController = (wrapper.vm as any).supportForm
    vm.setSupport(true)
    vm.viewerHandler.user.setX(genUser())
    await vm.$nextTick()
    supportForm.fields.body.update('This is a test.')
    await vm.$nextTick()
    const submit = dialogExpects({wrapper, formName: 'supportRequest', fields: ['email', 'body']})
    submit.trigger('click')
    const response = rq('/api/lib/v1/support/request/', 'post',
      {
        email: 'fox@artconomy.com',
        body: 'This is a test.',
        referring_url: '/',
      }, {})
    expect(mockAxios.request).toHaveBeenCalledWith(response)
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
      mocks: {$route: {fullPath: '/', params: {}, query: {}}, $router: {push: jest.fn()}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    })
    const vm = wrapper.vm as any
    const supportForm = vm.supportForm
    expect(supportForm.fields.email.value).toBe('')
    vm.setSupport(true)
    vm.viewerHandler.user.setX(genUser())
    await vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('fox@artconomy.com')
    const editedUser = genUser({email: 'test@example.com'})
    vm.viewerHandler.user.setX(editedUser)
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('test@example.com')
    vm.viewerHandler.user.setX(genAnon())
    await vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('')
  })
  it('Updates the email field when the viewer\'s guest email is updated.', async() => {
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}, $router: {push: jest.fn()}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    })
    const vm = wrapper.vm as any
    const supportForm = vm.supportForm
    expect(supportForm.fields.email.value).toBe('')
    vm.viewerHandler.user.setX(genUser())
    await vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('fox@artconomy.com')
    const editedUser = genUser({email: 'test@example.com', guest_email: 'test2@example.com'})
    vm.viewerHandler.user.setX(editedUser)
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.email.value).toBe('test2@example.com')
    vm.viewerHandler.user.setX(genAnon())
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
  it('Shows a reconnecting banner if we have lost connection', async() => {
    jest.useRealTimers()
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const server = new WS(wrapper.vm.$sock.endpoint)
    await server.connected
    server.close()
    await server.closed
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Reconnecting...')
  })
  it('Resets the connection', async() => {
    jest.useRealTimers()
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const vm = wrapper.vm
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    // Need to make sure the cookie for the socket key is set, which can happen on next tick.
    await vm.$nextTick()
    const mockClose = jest.spyOn(vm.$sock.socket!, 'close')
    const mockReconnect = jest.spyOn(vm.$sock.socket!, 'reconnect')
    await server.connected
    expect(mockClose).not.toHaveBeenCalled()
    expect(mockReconnect).not.toHaveBeenCalled()
    server.send({command: 'reset', payload: {}})
    await wrapper.vm.$nextTick()
    expect(mockClose).toHaveBeenCalledTimes(1)
    await new Promise((resolve) => setTimeout(resolve, 3000))
    expect(mockReconnect).toHaveBeenCalledTimes(1)
  })
  it('Sets the viewer', async() => {
    jest.useRealTimers()
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    await server.connected
    const person = genUser({username: 'Person'})
    server.send({command: 'viewer', payload: person})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.viewer.username).toBe('Person')
  })
  it('Gets the current version', async() => {
    jest.useRealTimers()
    wrapper = mount(App, {
      store,
      localVue,
      vuetify,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    })
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    await server.connected
    await expect(server).toReceiveMessage({command: 'version', payload: {}})
    server.send({command: 'version', payload: {version: 'beep'}})
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.socketState.x.serverVersion).toEqual('beep')
  })
})
