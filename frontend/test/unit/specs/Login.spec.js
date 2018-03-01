import Login from '@/components/Login'
import VueFormGenerator from 'vue-form-generator'
import VueRouter from 'vue-router'
import { router } from '../../../src/router'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import BootstrapVue from 'bootstrap-vue'
import { mount, createLocalVue } from 'vue-test-utils'
import sinon from 'sinon'
import { checkJson, isVisible } from '../helpers'
import { UserHandler } from '../../../src/plugins/user'

let server, localVue

describe('Login.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.use(VueRouter)
    localVue.use(BootstrapVue)
    localVue.use(UserHandler)
    localVue.use(VueFormGenerator)
  })
  afterEach(function () {
    server.restore()
  })
  it('Should send login information when filling out the login form and hitting the login button.', async () => {
    let wrapper = mount(Login, {
      localVue,
      router
    })
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    expect(wrapper.find('input[id="field-email"]').exists()).to.equal(true)
    expect(wrapper.find('input[id="field-password"]').exists()).to.equal(true)
    expect(isVisible(wrapper.find('#loginTab'))).to.equal(true)
    expect(isVisible(wrapper.find('#registerTab'))).to.equal(false)
    wrapper.vm.loginModel.email = 'jimbob@example.com'
    wrapper.vm.loginModel.password = 'hunter2'
    let loginSubmit = wrapper.find('#loginSubmit')
    expect(loginSubmit.text()).to.equal('Login')
    expect(loginSubmit.exists()).to.equal(true)
    loginSubmit.trigger('click')
    expect(server.requests.length, 1)
    checkJson(
      server.requests[0], {
        'data': {
          'email': 'jimbob@example.com', 'password': 'hunter2', 'username': '', 'recaptcha': ''
        },
        'url': '/api/profiles/v1/login/',
        'method': 'POST'
      })
  })
  it('Should send registration information when filling out the login form and hitting the register button.', async () => {
    let wrapper = mount(Login, {
      localVue,
      router
    })
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    wrapper.find('#registerTab___BV_tab_button__').trigger('click')
    await localVue.nextTick()
    // Force evaluation of computed properties, not running in test for some reason.
    wrapper.vm.$forceUpdate()
    let registerSubmit = wrapper.find('#loginSubmit')
    expect(registerSubmit.text()).to.equal('Register')
    expect(isVisible(wrapper.find('#loginTab'))).to.equal(false)
    expect(isVisible(wrapper.find('#registerTab'))).to.equal(true)
    wrapper.vm.loginModel.email = 'jimbob@example.com'
    wrapper.vm.loginModel.password = 'hunter2'
    wrapper.vm.loginModel.username = 'jimbob'
    registerSubmit.trigger('click')
    expect(server.requests.length, 1)
    checkJson(
      server.requests[0], {
        'data': {
          'email': 'jimbob@example.com', 'password': 'hunter2', 'username': 'jimbob', 'recaptcha': ''
        },
        'url': '/api/profiles/v1/register/',
        'method': 'POST'
      })
  })
})
