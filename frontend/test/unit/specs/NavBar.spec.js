import Vue from 'vue'
import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import BootstrapVue from 'bootstrap-vue'
import $ from 'jquery'

Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)

function waitFor (func, timeout) {
  return new Promise(function (resolve, reject) {
    let timer = 0;
    (function waitForCondition () {
      if (func()) return resolve()
      timer += 1
      if (timer >= timeout) {
        return reject(new Error('Timed out waiting for condition.'))
      }
      setTimeout(waitForCondition, 1)
    })()
  })
}

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
  it('Should display a login modal when clicking the login button', async() => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: {}}
      }
    ).$mount()
    await Vue.nextTick()
    let modal = vm.$el.querySelector('#loginModal')
    $(vm.$el.querySelector('#navbar .nav-login-item')).parent('a').click()
    return waitFor(
      function () {
        return $(modal).is(':visible')
      },
      3
    )
  })
})
