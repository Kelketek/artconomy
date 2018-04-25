import Login from '@/components/Login'
import VueFormGenerator from 'vue-form-generator'
import VueRouter from 'vue-router'
import { router } from '../../../src/router'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import { mount, createLocalVue } from '@vue/test-utils'
import sinon from 'sinon'
import { checkJson, installFields, isVisible } from '../helpers'
import { UserHandler } from '../../../src/plugins/user'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

let server, localVue

describe('Login.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.use(VueRouter)
    localVue.use(UserHandler)
    localVue.use(VueFormGenerator)
    localVue.use(Vuetify)
    installFields(localVue)
  })
  afterEach(function () {
    server.restore()
  })
  it('Should send login information when filling out the login form and hitting the login button.', async () => {
    router.replace({name: 'Login', params: {tabName: 'login'}})
    let wrapper = mount(Login, {
      localVue,
      router
    })
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    expect(wrapper.find('input[id="field-email"]').exists()).to.equal(true)
    expect(wrapper.find('input[id="field-password"]').exists()).to.equal(true)
    await localVue.nextTick()
    expect(isVisible(wrapper.find('#tab-login'))).to.equal(true)
    expect(isVisible(wrapper.find('#tab-register'))).to.equal(false)
    wrapper.vm.loginModel.email = 'jimbob@example.com'
    wrapper.vm.loginModel.password = 'hunter2'
    let loginSubmit = wrapper.find('#loginSubmit')
    expect(isVisible(loginSubmit)).to.equal(true)
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
})
