import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import BootstrapVue from 'bootstrap-vue'
import { mount, createLocalVue } from 'vue-test-utils'
import sinon from 'sinon'
import { checkJson, isVisible, waitFor } from '../helpers'
import { UserHandler } from '../../../src/plugins/user'

let server, localVue

describe('NavBar.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.use(BootstrapVue)
    localVue.use(UserHandler)
    localVue.use(VueFormGenerator)
  })
  afterEach(function () {
    server.restore()
  })
  it('should wait until the user is populated to show contents/', async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser(null)
    expect(wrapper.find('#nav_collapse').text())
      .to.equal('')
  })
  it('should show a login button when logged out', async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    expect(wrapper.find('#nav_collapse').text())
      .to.equal('Login')
  })
  it("Should show the logged in user's name when logged in.", async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser({username: 'Jimmy'})
    await localVue.nextTick()
    expect(wrapper.find('#navbar .nav-login-item').text())
      .to.equal('Jimmy')
  })
  it('Should show a login modal when the login button is clicked.', async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    let loginModal = wrapper.find('#loginModal')
    expect(isVisible(loginModal)).to.equal(false)
    wrapper.find('#navbar .nav-login-item').trigger('click')
    await localVue.nextTick()
    expect(loginModal.exists()).to.equal(true)
    await waitFor(() => { return isVisible(loginModal) }, 'Login modal is shown.')
    expect(isVisible(loginModal)).to.equal(true)
  })
  it('Should send login information when filling out the login form and hitting the login button.', async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    wrapper.find('#navbar .nav-login-item').trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('input[id="email"]').exists()).to.equal(true)
    expect(wrapper.find('input[id="password"]').exists()).to.equal(true)
    expect(isVisible(wrapper.find('#loginTab'))).to.equal(true)
    expect(isVisible(wrapper.find('#registerTab'))).to.equal(false)
    expect(isVisible(wrapper.find('#loginCancel'))).to.equal(true)
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
          'email': 'jimbob@example.com', 'password': 'hunter2', 'username': ''
        },
        'url': '/api/profiles/v1/login/',
        'method': 'POST'
      })
  })
  it('Should send registration information when filling out the login form and hitting the register button.', async () => {
    let wrapper = mount(NavBar, {localVue})
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    wrapper.find('#navbar .nav-login-item').trigger('click')
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
          'email': 'jimbob@example.com', 'password': 'hunter2', 'username': 'jimbob'
        },
        'url': '/api/profiles/v1/register/',
        'method': 'POST'
      })
  })
})
