import Vue from 'vue'
import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import BootstrapVue from 'bootstrap-vue'

Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)

describe('NavBar.vue', () => {
  it('should wait until the user is populated to show contents/', async () => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: null}
      }
    ).$mount()
    await Vue.nextTick()
    expect(vm.$el.querySelector('#nav_collapse').textContent)
      .to.equal('')
  })
  it('should show a login button when logged out', async () => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: {}}
      }
    ).$mount()
    await Vue.nextTick()
    expect(vm.$el.querySelector('#navbar .nav-login-item').textContent)
      .to.equal('Login')
  })
  it("Should show the logged in user's name when logged in.", async () => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: {username: 'Jimmy'}}
      }
    ).$mount()
    await Vue.nextTick()
    expect(vm.$el.querySelector('#navbar .nav-login-item').textContent)
      .to.equal('Jimmy')
  })
  it('Should display a login modal when clicking the login button.', async () => {
    console.log('I ran!')
  })
})
