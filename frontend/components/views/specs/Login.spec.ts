import Vue from 'vue'
import {shallowMount, Wrapper} from '@vue/test-utils'
import Login from '../Login.vue'
import {ArtStore, createStore} from '@/store'
import mockAxios from '@/specs/helpers/mock-axios'
import {cleanUp, createVuetify, docTarget, expectFields, fieldEl, makeSpace, vueSetup, mount} from '@/specs/helpers'
import {userResponse} from '@/specs/helpers/fixtures'
import flushPromises from 'flush-promises'
import {deleteCookie} from '@/lib/lib'
import {UserStoreState} from '@/store/profiles/types/UserStoreState'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let profiles: UserStoreState
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

Element.prototype.scrollIntoView = jest.fn()
const mockTrace = jest.spyOn(console, 'trace')

describe('Login.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
    deleteCookie('csrftoken')
    vuetify = createVuetify()
    profiles = (store.state as any).profiles as UserStoreState
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Initializes', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {replace: jest.fn()}, $route: {name: 'Login', params: {}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    expect((wrapper.vm as any).loginTab).toBe('')
  })
  it('Sends login info', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    const fields = wrapper.vm.$getForm('login').fields
    expectFields(fields, ['email', 'password', 'token', 'order_claim'])
    fields.email.update('test@example.com', false)
    fields.password.update('pass', false)
    await wrapper.vm.$nextTick()
    const email = wrapper.find('#field-login__email')
    const password = wrapper.find('#field-login__password')
    expect((email.element as HTMLInputElement).value).toBe('test@example.com')
    expect((password.element as HTMLInputElement).value).toBe('pass')
    const submit = wrapper.find('#loginSubmit')
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledTimes(1)
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/api/profiles/v1/login/',
      {email: 'test@example.com', password: 'pass', token: ''},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    )
  })
  it('Retrieves and sends an order token', () => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {
        $router: {},
        $route: {name: 'Login', params: {tabName: 'login'}, query: {claim: '0e59f96e-700f-48f0-ac13-f565846497d5'}},
      },
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    const fields = wrapper.vm.$getForm('login').fields
    expect(fields.order_claim.value).toBe('0e59f96e-700f-48f0-ac13-f565846497d5')
  })
  it('Retrieves and sends artist mode toggle', () => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {
        $router: {replace: jest.fn()},
        $route: {name: 'Login', params: {}, query: {artist_mode: 'true'}},
      },
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    const fields = wrapper.vm.$getForm('register').fields
    expect(fields.artist_mode.value).toBe(true)
  })
  it('Logs in the user', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledTimes(1)
    const response = userResponse()
    // const user = response.data
    mockAxios.mockResponse(response)
    await flushPromises()
    expect((wrapper.vm as any).viewer).toEqual(response.data)
  })
  it('Handles a network error', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    const submit = wrapper.find('#loginSubmit')
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledTimes(1)
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError({})
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  it('Handles a general server error', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    await wrapper.vm.$nextTick()
    const submit = wrapper.find('#loginSubmit')
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledTimes(1)
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError({response: {}})
    await flushPromises()
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  it('Sends the user home by default on login', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(push).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith({name: 'Home'})
  })
  it('Redirects the user to the "next" variable on login', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {next: '/destination/'}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(push).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith('/destination/')
  })
  it('Redirects the user to their profile is the next variable is /.', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {next: '/'}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(push).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith({name: 'Profile', params: {username: 'Fox'}})
  })
  it('Handles a failed login', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: jest.fn(), $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    mockAxios.reset()
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    const submit = wrapper.find('#loginSubmit')
    submit.trigger('click')
    mockAxios.mockError!({response: {data: {email: ['Nope.']}}})
    await flushPromises()
    expect((wrapper.vm as any).showTokenPrompt).toBe(false)
    expect(controller.fields.email.errors).toEqual(['Nope.'])
  })
  it('Syncs the value of the email field', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: jest.fn(), $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    const otherController = wrapper.vm.$getForm('register')
    await wrapper.vm.$nextTick()
    expect(otherController.fields.email.value).toBe(controller.fields.email.value)
  })
  it('Prompts for a second attempt with 2FA', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: jest.fn(), $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    expect((wrapper.vm as any).showTokenPrompt).toBe(false)
    mockAxios.reset()
    const submit = wrapper.find('#loginSubmit')
    submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: ['Please provide your login token.']}}})
    await flushPromises()
    expect((wrapper.vm as any).showTokenPrompt).toBe(true)
    // On the first failure, we don't want to show errors since they're part of the normal login process.
    expect(controller.fields.token.errors).toEqual([])
  })
  it('Does not prompt for 2FA if the token error field is empty.', async() => {
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: jest.fn(), $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    expect((wrapper.vm as any).showTokenPrompt).toBe(false)
    mockAxios.reset()
    const submit = wrapper.find('#loginSubmit')
    submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: []}}})
    await flushPromises()
    expect((wrapper.vm as any).showTokenPrompt).toBe(false)
  })
  it('Accepts and sends 2FA Token', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'login'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    controller.fields.token.update('086456', false);
    (wrapper.vm as any).showTokenPrompt = true
    await wrapper.vm.$nextTick()
    const submit = wrapper.find('#tokenSubmit')
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/api/profiles/v1/login/',
      {email: 'test@example.com', password: 'pass', token: '086 456'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    )
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    // On the first failure, we don't want to show errors since they're part of the normal login process.
    expect(push).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith({name: 'Home'})
  })
  it('Handles a 2FA failure', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push, replace: jest.fn()}, $route: {name: 'Login', params: {}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const fields = wrapper.vm.$getForm('login').fields;
    (wrapper.vm as any).showTokenPrompt = true
    await wrapper.vm.$nextTick()
    const submit = wrapper.find('#tokenSubmit')
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockError({response: {data: {token: ['Stuff!']}}})
    await flushPromises()
    expect(fields.token.errors).toEqual(['Stuff!']);
    // Get that last bit of code coverage.
    (wrapper.vm as any).showTokenPrompt = false
  })
  it('Has a registration form', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'register'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    expect((wrapper.vm as any).loginTab).toBe('tab-register')
    const fields = wrapper.vm.$getForm('register').fields
    expectFields(fields, [
      'username', 'email', 'password', 'registration_code', 'order_claim', 'mail', 'recaptcha',
    ])
    await wrapper.vm.$nextTick()
    expect(fields.mail.value).toBe(true)
    fields.username.update('Goofball', false)
    fields.email.update('test@example.com', false)
    fields.password.update('secret', false)
    fields.mail.update(false, false)
    fields.registration_code.update('BLEP', false)
    await wrapper.vm.$nextTick()
    const username = fieldEl(wrapper, fields.username)
    const email = fieldEl(wrapper, fields.email)
    const password = fieldEl(wrapper, fields.password)
    const registrationCode = fieldEl(wrapper, fields.registration_code)
    expect(fields.email.value).toBe('test@example.com')
    expect(email.value).toBe('test@example.com')
    expect(password.value).toBe('secret')
    expect(username.value).toBe('Goofball')
    expect(registrationCode.value).toBe('BLEP')
  })
  it('Submits a registration form', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'register'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const fields = wrapper.vm.$getForm('register').fields
    fields.username.update('Goofball', false)
    fields.email.update('test@example.com', false)
    fields.password.update('secret', false)
    fields.mail.update(false, false)
    fields.registration_code.update('BLEP', false)
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/api/profiles/v1/register/',
      {
        email: 'test@example.com',
        mail: false,
        password: 'secret',
        recaptcha: '',
        registration_code: 'BLEP',
        username: 'Goofball',
        artist_mode: false,
      },
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    )
  })
  it('Handles a failed registration', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'register'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const form = wrapper.vm.$getForm('register')
    const fields = form.fields
    fields.username.update('Goofball', false)
    fields.recaptcha.update('234dfsdfjv', false)
    expect(fields.recaptcha.value).toBe('234dfsdfjv')
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockError!({response: {data: {username: ['Too silly.'], recaptcha: ['Wrong.']}}})
    await flushPromises()
    expect(fields.recaptcha.value).toBe('')
  })
  it('Handles a successful registration', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'register'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(push).toHaveBeenCalledWith({name: 'Profile', params: {username: 'Fox'}, query: {editing: 'true'}})
  })
  it('Has a forgot password form', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'forgot'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    await wrapper.vm.$nextTick()
    const fields = wrapper.vm.$getForm('forgot').fields
    expect((wrapper.vm as any).loginTab).toBe('tab-forgot')
    expectFields(fields, ['email'])
    fields.email.update('Test', false)
    await wrapper.vm.$nextTick()
    const forgotField = fieldEl(wrapper, fields.email)
    expect(forgotField.value).toBe('Test')
  })
  it('Submits a forgot password form', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'forgot'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),

    })
    const fields = wrapper.vm.$getForm('forgot').fields
    fields.email.update('Test', false)
    const submit = wrapper.find('#forgotSubmit')
    mockAxios.reset()
    submit.trigger('click')
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/api/profiles/v1/forgot-password/',
      {
        email: 'Test',
      },
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    )
  })
  it('Handles a forgotten password response', async() => {
    const push = jest.fn()
    wrapper = mount(Login, {
      store,
      localVue,
      vuetify,
      mocks: {$router: {push}, $route: {name: 'Login', params: {tabName: 'forgot'}, query: {}}},
      stubs: ['router-link'],
      attachTo: docTarget(),
    })
    const submit = wrapper.find('#forgotSubmit')
    mockAxios.reset()
    submit.trigger('click')
    mockAxios.mockResponse({data: undefined, status: 204})
    await flushPromises()
  })
})
