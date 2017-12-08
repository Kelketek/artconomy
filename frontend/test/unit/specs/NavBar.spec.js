import Vue from 'vue'
import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import BootstrapVue from 'bootstrap-vue'

Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)

describe('NavBar.vue', () => {
  it('should wait until the user is populated to show contents/', done => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: null}
      }
    ).$mount()
    Vue.nextTick(() => {
      expect(vm.$el.querySelector('#nav_collapse').textContent)
        .to.equal('')
      done()
    })
  })
  it('should show a login button when logged out', done => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: {}}
      }
    ).$mount()
    Vue.nextTick(() => {
      expect(vm.$el.querySelector('#navbar .nav-login-item').textContent)
        .to.equal('Login')
      done()
    })
  })
  it("Should show the logged in user's name when logged in.", done => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: {username: 'Jimmy'}}
      }
    ).$mount()
    Vue.nextTick(() => {
      expect(vm.$el.querySelector('#navbar .nav-login-item').textContent)
        .to.equal('Jimmy')
      done()
    })
  })
})
