import {VueWrapper} from '@vue/test-utils'
import Login from '../Login.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import {cleanUp, expectFields, fieldEl, mount, rq, vueSetup, VuetifyWrapped, waitFor} from '@/specs/helpers/index.ts'
import {userResponse} from '@/specs/helpers/fixtures.ts'
import flushPromises from 'flush-promises'
import {deleteCookie} from '@/lib/lib.ts'
import {UserStoreState} from '@/store/profiles/types/UserStoreState.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {createRouter, createWebHistory, Router} from 'vue-router'
import AuthViews from '@/components/views/auth/AuthViews.vue'
import Register from '@/components/views/auth/Register.vue'
import Forgot from '@/components/views/auth/Forgot.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'

let profiles: UserStoreState
let wrapper: VueWrapper<any>
let router: Router

Element.prototype.scrollIntoView = vi.fn()
const mockTrace = vi.spyOn(console, 'trace')

const WrappedViews = VuetifyWrapped(AuthViews)

describe('AuthViews.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        path: '/auth/',
        component: AuthViews,
        children: [{
          name: 'AuthViews',
          path: '',
          redirect: {name: 'Login'},
        }, {
          path: 'login/',
          name: 'Login',
          component: Login,
        }, {
          path: 'register/',
          name: 'Register',
          component: Register,
        }, {
          path: 'forgot/',
          name: 'Forgot',
          component: Forgot,
        }],
      }, {
        path: '/profiles/:username',
        name: 'Profile',
        component: Empty,
      }, {
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/destination/',
        name: 'Destination',
        component: Empty,
      }, {
        path: '/legal/privacy/',
        name: 'PrivacyPolicy',
        component: Empty,
      }, {
        path: '/legal/terms/',
        name: 'TermsOfService',
        component: Empty,
      }],
    })
    store = createStore()
    deleteCookie('csrftoken')
    profiles = (store.state as any).profiles as UserStoreState
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Initializes', async() => {
    await router.push({name: 'Login'})
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
  })
  test('Sends login info', async() => {
    await router.push({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
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
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/login/',
      'post',
      {
        email: 'test@example.com',
        password: 'pass',
        token: '',
      },
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    ))
  })
  test('Retrieves and sends an order token', async() => {
    await router.replace({
      name: 'Login',
      query: {claim: '0e59f96e-700f-48f0-ac13-f565846497d5'},
    })
    wrapper = mount(AuthViews, {
      ...vueSetup({
        store,
        router,
      }),
    })
    const fields = wrapper.vm.$getForm('login').fields
    expect(fields.order_claim.value).toBe('0e59f96e-700f-48f0-ac13-f565846497d5')
  })
  test('Retrieves and sends artist mode toggle', async() => {
    await router.replace({
      name: 'Login',
      params: {},
      query: {artist_mode: 'true'},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
      stubs: ['router-link'],
    }))
    const fields = wrapper.vm.$getForm('register').fields
    expect(fields.artist_mode.value).toBe(true)
  })
  test('Logs in the user', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    const response = userResponse()
    // const user = response.data
    mockAxios.mockResponse(response)
    await flushPromises()
    expect((wrapper.vm as any).viewer).toEqual(response.data)
  })
  test('Handles a network error', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    const submit = wrapper.find('#loginSubmit')
    await wrapper.vm.$nextTick()
    mockAxios.reset()
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError({})
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  test('Handles a general server error', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    await wrapper.vm.$nextTick()
    const submit = wrapper.find('#loginSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError({response: {}})
    await flushPromises()
    expect(controller.errors).toEqual(['We had an issue contacting the server. Please try again later!'])
    expect(mockTrace).toHaveBeenCalled()
  })
  test('Sends the user home by default on login', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('Home')
  })
  test('Redirects the user to the "next" variable on login', async() => {
    await router.replace({
      name: 'Login',
      query: {next: '/destination/'},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(router.currentRoute.value.fullPath, '/destination/')
  })
  test('Redirects the user to their profile is the next variable is /.', async() => {
    await router.replace({
      name: 'Login',
      query: {next: '/'},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#loginSubmit')
    expect((wrapper.vm as any).viewer).toBe(null)
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await wrapper.vm.$nextTick()
    await flushPromises()
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Profile'))
    expect(router.currentRoute.value.params).toEqual({username: 'Fox'})
  })
  test('Handles a failed login', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    mockAxios.reset()
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    const submit = wrapper.find('#loginSubmit')
    await submit.trigger('click')
    mockAxios.mockError!({response: {data: {email: ['Nope.']}}})
    await flushPromises()
    expect(controller.fields.email.errors).toEqual(['Nope.'])
  })
  test('Syncs the value of the email field', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(AuthViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    const otherController = wrapper.vm.$getForm('register')
    await wrapper.vm.$nextTick()
    expect(otherController.fields.email.value).toBe(controller.fields.email.value)
  })
  test('Prompts for a second attempt with 2FA', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    expect(wrapper.find('.token-prompt-loaded').exists()).toBe(false)
    mockAxios.reset()
    const submit = wrapper.find('#loginSubmit')
    await submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: ['Please provide your login token.']}}})
    await flushPromises()
    expect(wrapper.findComponent('.token-prompt-loaded').exists()).toBe(true)
    // On the first failure, we don't want to show errors since they're part of the normal login process.
    expect(controller.fields.token.errors).toEqual([])
  })
  test('Does not prompt for 2FA if the token error field is empty.', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    expect(wrapper.find('.token-prompt-loaded').exists()).toBe(false)
    mockAxios.reset()
    const submit = wrapper.find('#loginSubmit')
    await submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: []}}})
    await flushPromises()
    expect(wrapper.find('.token-prompt-loaded').exists()).toBe(false)
  })
  test('Accepts and sends 2FA Token', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const controller = wrapper.vm.$getForm('login')
    controller.fields.email.update('test@example.com', false)
    controller.fields.password.update('pass', false)
    const submit = wrapper.find('#loginSubmit')
    await submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: ['Please provide your login token.']}}})
    await flushPromises()
    mockAxios.reset()
    controller.fields.token.update('086456', false)
    const submitToken = wrapper.findComponent('#tokenSubmit')
    await submitToken.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/login/',
      'post',
      {
        email: 'test@example.com',
        password: 'pass',
        token: '086456',
      },
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    ))
    mockAxios.mockResponse(userResponse())
    // On the first failure, we don't want to show errors since they're part of the normal login process.
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Home'))
  })
  test('Handles a 2FA failure', async() => {
    await router.replace({
      name: 'Login',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const fields = wrapper.vm.$getForm('login').fields
    const submit = wrapper.find('#loginSubmit')
    await submit.trigger('click')
    mockAxios.mockError!({response: {data: {token: ['Please provide your login token.']}}})
    await flushPromises()
    const tokenSubmit = wrapper.findComponent('#tokenSubmit')
    mockAxios.reset()
    await tokenSubmit.trigger('click')
    mockAxios.mockError({response: {data: {token: ['Stuff!']}}})
    await flushPromises()
    expect(fields.token.errors).toEqual(['Stuff!'])
  })
  test('Has a registration form', async() => {
    await router.replace({
      name: 'Register',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    expect(wrapper.find('.registration-page').exists()).toBe(true)
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
  test('Submits a registration form', async() => {
    await router.replace({
      name: 'Register',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const fields = wrapper.vm.$getForm('register').fields
    fields.username.update('Goofball', false)
    fields.email.update('test@example.com', false)
    fields.password.update('secret', false)
    fields.mail.update(false, false)
    fields.registration_code.update('BLEP', false)
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/register/',
      'post',
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
    ))
  })
  test('Handles a failed registration', async() => {
    await router.replace({
      name: 'Register',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const form = wrapper.vm.$getForm('register')
    const fields = form.fields
    fields.username.update('Goofball', false)
    fields.recaptcha.update('234dfsdfjv', false)
    expect(fields.recaptcha.value).toBe('234dfsdfjv')
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockError!({
      response: {
        data: {
          username: ['Too silly.'],
          recaptcha: ['Wrong.'],
        },
      },
    })
    await flushPromises()
    expect(fields.recaptcha.value).toBe('')
  })
  test('Handles a successful registration', async() => {
    await router.replace({
      name: 'Register',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#registerSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('Profile')
    expect(router.currentRoute.value.params).toEqual({username: 'Fox'})
    expect(router.currentRoute.value.query).toEqual({editing: 'true'})
  })
  test('Has a forgot password form', async() => {
    await router.replace({
      name: 'Forgot',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    await wrapper.vm.$nextTick()
    const fields = wrapper.vm.$getForm('forgot').fields
    expect(wrapper.find('.forgot-page').exists()).toBe(true)
    expectFields(fields, ['email'])
    fields.email.update('Test', false)
    await wrapper.vm.$nextTick()
    const forgotField = fieldEl(wrapper, fields.email)
    expect(forgotField.value).toBe('Test')
  })
  test('Submits a forgot password form', async() => {
    await router.replace({
      name: 'Forgot',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const fields = wrapper.vm.$getForm('forgot').fields
    fields.email.update('Test', false)
    const submit = wrapper.find('#forgotSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/api/profiles/forgot-password/',
      'post',
      {
        email: 'Test',
      },
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    ))
  })
  test('Handles a forgotten password response', async() => {
    await router.replace({
      name: 'Forgot',
      query: {},
    })
    wrapper = mount(WrappedViews, vueSetup({
      store,
      router,
    }))
    const submit = wrapper.find('#forgotSubmit')
    mockAxios.reset()
    await submit.trigger('click')
    mockAxios.mockResponse({
      data: undefined,
      status: 204,
    })
    await flushPromises()
  })
})
