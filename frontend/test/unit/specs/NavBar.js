import Vue from 'vue'
import NavBar from '@/components/NavBar'

describe('NavBar.vue', () => {
  it('should show a login button', () => {
    const Constructor = Vue.extend(NavBar)
    const vm = new Constructor().$mount()
    expect(vm.$el.querySelector('#navbar .nav-item').textContent)
      .toEqual('Login')
  })
})
