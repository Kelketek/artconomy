import Vue from 'vue'
import NavBar from '@/components/NavBar'
import VueFormGenerator from 'vue-form-generator'
import BootstrapVue from 'bootstrap-vue'

Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)

describe('NavBar.vue', () => {
  it('should show a login button', () => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor(
      {
        propsData: {user: null}
      }
    ).$mount()
    expect(vm.$el.querySelector('#navbar .nav-item').textContent)
      .toEqual('Login')
  })
})
