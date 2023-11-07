import mockAxios from './helpers/mock-axios'
import {VueWrapper} from '@vue/test-utils'
import App from '../App.vue'
import {ArtStore, createStore} from '@/store'
import flushPromises from 'flush-promises'
import {genUser} from './helpers/fixtures'
import {FormController} from '@/store/forms/form-controller'
import {cleanUp, dialogExpects, docTarget, genAnon, mount, rq, rs, vueSetup, waitFor} from './helpers'
import {WS} from 'vitest-websocket-mock'
import {socketNameSpace} from '@/plugins/socket'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {reactive} from 'vue'

let wrapper: VueWrapper<any>

// @ts-ignore
window.__COMMIT_HASH__ = 'bogusHash'
socketNameSpace.socketClass = WebSocket

describe('App.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Detects when a full interface should not be used due to a specific name', async() => {
    wrapper = mount(
      App,
      vueSetup({
        store,
        mocks: {$route: {fullPath: '/order/', name: 'NewOrder', params: {}, query: {}}},
        stubs: ['nav-bar', 'router-view', 'router-link'],
      }))
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(false)
  })
  test('Detects when a full interface should not be used due to a landing page', async() => {
    wrapper = mount(App, vueSetup({
        store,
        mocks: {$route: {fullPath: '/order/', name: 'LandingStuff', params: {}, query: {}}},
        stubs: ['nav-bar', 'router-view', 'router-link'],
      }))
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(false)
  })
  test('Detects when a full interface should be used', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/order/', name: 'Thingsf', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
    }))
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(true)
  })
  test('Detects when a full interface should be used on a broken route', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/order/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
    }))
    const vm = wrapper.vm as any
    expect(vm.fullInterface).toBe(true)
  })
  test('Opens and closes an age verification dialog', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/order/', params: {}, query: {}}},
      stubs: ['nav-bar', 'router-view', 'router-link'],
    }))
    const vm = wrapper.vm as any
    vm.viewerHandler.user.makeReady(genUser())
    store.commit('setShowAgeVerification', true)
    await vm.$nextTick()
    expect(store.state.showAgeVerification).toBe(true)
    expect(vm.viewerHandler.user.x).toBeTruthy()
    wrapper.find('.dialog-closer').trigger('click')
    await vm.$nextTick()
    expect(wrapper.find('dialog-closer').exists()).toBe(false)
  })
  test('Submits the support request form', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    }))
    const state = wrapper.vm.$store.state
    expect(state.showSupport).toBe(false)
    const vm = wrapper.vm as any
    expect(vm.showTicketSuccess).toBe(false)
    const supportForm: FormController = (wrapper.vm as any).supportForm
    vm.$store.commit('supportDialog', true)
    vm.viewerHandler.user.setX(genUser())
    await vm.$nextTick()
    supportForm.fields.body.update('This is a test.')
    await vm.$nextTick()
    const submit = dialogExpects({wrapper, formName: 'supportRequest', fields: ['email', 'body']})
    submit.trigger('click')
    const response = rq('/api/lib/support/request/', 'post',
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
  test('Updates the email field when the viewer\'s email is updated.', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}, $router: {push: vi.fn()}},
      stubs: ['router-link', 'router-view', 'nav-bar'],

    }))
    const vm = wrapper.vm as any
    const supportForm = vm.supportForm
    expect(supportForm.fields.email.value).toBe('')
    vm.$store.commit('supportDialog', true)
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
  test('Updates the email field when the viewer\'s guest email is updated.', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}, $router: {push: vi.fn()}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
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
  test('Updates the referring_url field when the route has changed.', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: reactive({$route: {fullPath: '/', params: {}, query: {}}}),
      stubs: ['router-link', 'router-view', 'nav-bar']
    }))
    const supportForm = (wrapper.vm as any).supportForm
    expect(supportForm.fields.referring_url.value).toBe('/')
    wrapper.vm.$route.fullPath = '/test/'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(supportForm.fields.referring_url.value).toBe('/test/')
  })
  test('Shows an alert', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    console.log(wrapper.html())
    expect(wrapper.find('#alert-bar').exists()).toBe(true)
  })
  test('Removes an alert automatically', async() => {
    // NOTE: This test causes issues with timer cleanup, but there appears to be
    // no solution for this now. The error given by jest about clearing native
    // timers can safely be ignored. The next few tests may also be affected by
    // this issue.
    vi.useFakeTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    vi.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    vi.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#alert-bar').exists()).toBe(false)
    expect((wrapper.vm as any).showAlert).toBe(false)
  })
  test('Resets the alert dismissal value after the alert has cleared.', async() => {
    vi.useFakeTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    store.commit('pushAlert', {message: 'I am an alert!', category: 'error'})
    await wrapper.vm.$nextTick()
    vi.runOnlyPendingTimers()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).alertDismissed).toBe(false)
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })
  test('Manually resets alert dismissal, if needed', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    wrapper.vm.alertDismissed = true;
    wrapper.vm.showAlert = true
    expect((wrapper.vm as any).alertDismissed).toBe(false)
  })
  test('Loads up search form data', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: reactive({$route: {fullPath: '/', params: {}, query: {q: 'Stuff', featured: 'true'}, name: null}}),
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    const vm = wrapper.vm as any
    vm.$route.name = 'Home'
    await vm.$nextTick()
    expect(vm.searchForm.fields.q.value).toBe('Stuff')
  })
  test('Shows the markdown help section', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    const vm = wrapper.vm as any
    await wrapper.vm.$nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.find('.markdown-rendered-help').exists()).toBe(false)
    vm.showMarkdownHelp = true
    await wrapper.vm.$nextTick()
    await waitFor(() => expect(wrapper.find('.markdown-rendered-help').exists()).toBe(true))
    expect(store.state.markdownHelp).toBe(true)
    wrapper.find('#close-markdown-help').trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.markdownHelp).toBe(false)
    expect(wrapper.find('.markdown-rendered-help').exists()).toBe(true)
  })
  test('Changes the route key', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: reactive({$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}}),
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.routeKey).toEqual('')
    vm.$route.params.username = 'Bob'
    expect(vm.routeKey).toEqual('username:Bob|')
    vm.$route.params.characterName = 'Dude'
    expect(vm.routeKey).toEqual('characterName:Dude|username:Bob|')
    vm.$route.params.submissionId = '555'
    expect(vm.routeKey).toEqual('characterName:Dude|submissionId:555|username:Bob|')
  })
  test('Determines whether or not we are in dev mode', async() => {
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
    }))
    const vm = wrapper.vm as any
    expect(vm.mode()).toBe('test')
    expect(vm.devMode).toBe(false)
    const mockMode = vi.spyOn(vm, 'mode')
    mockMode.mockImplementation(() => 'development')
    expect(vm.mode()).toBe('development')
    vm.forceRecompute += 1
    await vm.$nextTick()
    expect(vm.devMode).toBe(true)
  })
  test('Shows a reconnecting banner if we have lost connection', async() => {
    vi.useRealTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar', 'ac-cookie-consent'],
    }))
    const server = new WS(wrapper.vm.$sock.endpoint)
    await server.connected
    wrapper.vm.socketState.updateX({serverVersion: 'beep'})
    server.close()
    await server.closed
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Reconnecting...')
  })
  test('Resets the connection', async() => {
    vi.useRealTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    }))
    const vm = wrapper.vm
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    // Need to make sure the cookie for the socket key is set, which can happen on next tick.
    await vm.$nextTick()
    const mockClose = vi.spyOn(vm.$sock.socket!, 'close')
    const mockReconnect = vi.spyOn(vm.$sock.socket!, 'reconnect')
    await server.connected
    expect(mockClose).not.toHaveBeenCalled()
    expect(mockReconnect).not.toHaveBeenCalled()
    server.send({command: 'reset', payload: {}})
    await wrapper.vm.$nextTick()
    expect(mockClose).toHaveBeenCalledTimes(1)
    await new Promise((resolve) => setTimeout(resolve, 3000))
    expect(mockReconnect).toHaveBeenCalledTimes(1)
  })
  test('Sets the viewer', async() => {
    vi.useRealTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    }))
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    await server.connected
    const person = genUser({username: 'Person'})
    server.send({command: 'viewer', payload: person})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.viewer.username).toBe('Person')
  })
  test('Gets the current version', async() => {
    vi.useRealTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: {$route: {fullPath: '/', params: {stuff: 'things'}, query: {}}},
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    }))
    const server = new WS(wrapper.vm.$sock.endpoint, {jsonProtocol: true})
    await server.connected
    await expect(server).toReceiveMessage({command: 'version', payload: {}})
    server.send({command: 'version', payload: {version: 'beep'}})
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.socketState.x.serverVersion).toEqual('beep')
  })
  test('Emits a tracking event', async() => {
    vi.useRealTimers()
    wrapper = mount(App, vueSetup({
      store,
      mocks: reactive({$route: {fullPath: '/', params: {stuff: 'things'}, name: 'Home', query: {}}}),
      stubs: ['router-link', 'router-view', 'nav-bar'],
      attachTo: docTarget(),
    }))
    await wrapper.vm.$nextTick()
    window._paq = []
    wrapper.vm.$route.fullPath = '/test/'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(window._paq).toEqual([
      ['setCustomUrl', 'http://localhost:3000/test/'],
      ['setDocumentTitle', ''],
      ['setReferrerUrl', 'http://localhost:3000/'],
      ['trackPageView'],
    ])
    window._paq = []
    // Should not send a tracking event, but others should be tracked.
    wrapper.vm.$route.name = 'FAQ'
    wrapper.vm.$route.fullPath = '/test/faq/'
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(window._paq).toEqual([
      ['setCustomUrl', 'http://localhost:3000/test/faq/'],
      ['setDocumentTitle', ''],
      ['setReferrerUrl', 'http://localhost:3000/test/'],
    ])
  })
})
