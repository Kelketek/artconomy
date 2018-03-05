import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import VueRouter from 'vue-router'
import { router } from '../../../src/router'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import BootstrapVue from 'bootstrap-vue'
import { mount, createLocalVue } from 'vue-test-utils'
import sinon from 'sinon'
import { UserHandler } from '../../../src/plugins/user'

let server, localVue

describe('NavBar.vue', () => {
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
  it('should wait until the user is populated to show contents', async () => {
    let wrapper = mount(
      NavBar, {
        localVue,
        router
      })
    wrapper.vm.$forceUser(null)
    await localVue.nextTick()
    expect(wrapper.find('.nav-login-item').text())
      .to.equal('')
  })
  it('should show a login button when logged out', async () => {
    let wrapper = mount(
      NavBar, {
        localVue,
        router
      })
    wrapper.vm.$forceUser({})
    await localVue.nextTick()
    expect(wrapper.find('.nav-login-item').text())
      .to.equal('Login')
  })
  it("Should show the logged in user's name when logged in.", async () => {
    let wrapper = mount(NavBar, {
      localVue,
      router
    })
    wrapper.vm.$forceUser({username: 'Jimmy'})
    await localVue.nextTick()
    expect(wrapper.find('.nav-login-item').text())
      .to.equal('Jimmy')
  })
})
