import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, shallowMount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import VueRouter from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {setViewer, vuetifySetup} from '@/specs/helpers'
import Credentials from '../Credentials.vue'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import Settings from '../Settings.vue'
import {listRegistry, Lists} from '@/store/lists/registry'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
jest.useFakeTimers()

const settingRoutes = [{
  path: '/profile/:username/settings/',
  name: 'Settings',
  component: Settings,
  props: true,
  meta: {
    sideNav: true,
  },
  children: [
    {
      name: 'Credentials',
      path: 'credentials',
      component: Credentials,
      props: true,
    },
  ],
}]

describe('Credentials.vue', () => {
  const localVue: VueConstructor = createLocalVue()
  localVue.use(Vuex)
  localVue.use(FormControllers)
  localVue.use(Lists)
  localVue.use(Singles)
  localVue.use(Profiles)
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  let router: VueRouter
  beforeEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    formRegistry.reset()
    listRegistry.reset()
    localVue.use(VueRouter)
    store = createStore()
    router = new VueRouter({
      mode: 'history',
      routes: settingRoutes,
    })
    vuetifySetup()
  })
  it('Mounts the credentials page', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    await wrapper.vm.$nextTick()
  })
  it('Updates the url', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(Credentials, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    const vm = wrapper.vm as any
    expect(vm.url).toBe('/api/profiles/v1/account/Fox/auth/credentials/')
    vm.subjectHandler.user.updateX({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    const newUrl = '/api/profiles/v1/account/Vulpes/auth/credentials/'
    expect(vm.url).toBe(newUrl)
    expect(vm.usernameForm.endpoint).toBe(newUrl)
    expect(vm.passwordForm.endpoint).toBe(newUrl)
    expect(vm.emailForm.endpoint).toBe(newUrl)
  })
  it('Disables the email submit button if the current password is missing', async() => {
    setViewer(store, genUser())
    wrapper = shallowMount(Credentials, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    const vm = wrapper.vm as any
    vm.emailForm.fields.email.update('test@example.com')
    vm.emailForm.fields.email2.update('test@example.com')
    await vm.$nextTick()
    expect(vm.emailDisabled).toBe(true)
  })
  it.each`
    currentPassword   | email                 | email2                | disabled | result
    ${''}             | ${''}                 | ${'test@example.com'} | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${''}                 | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${true}  | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${false} | ${false}
  `('should set emailDisabled $result when email is $email and email2 is ' +
    '$email2 and current_password is $currentPassword and form disability ' +
    'is $disabled', async({currentPassword, email, email2, disabled, result}) => {
  setViewer(store, genUser())
  wrapper = shallowMount(Credentials, {
    localVue,
    store,
    propsData: {username: 'Fox'},
    attachToDocument: true,
    sync: false,
  })
  const vm = wrapper.vm as any
  vm.emailForm.fields.current_password.update(currentPassword)
  vm.emailForm.fields.email.update(email)
  vm.emailForm.fields.email2.update(email2)
  store.commit('forms/updateMeta', {name: 'emailChange', meta: {disabled}})
  await vm.$nextTick()
  expect(vm.emailDisabled).toBe(result)
})
  it.each`
    currentPassword   | password              | password2             | disabled | result
    ${''}             | ${''}                 | ${'test@example.com'} | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${''}                 | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example2.com'}| ${true}  | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${false} | ${false}
  `('should set emailDisabled $result when new_password is $password and new_password2 is ' +
    '$new_password2 and current_password is $currentPassword and form disability is $disabled',
async({currentPassword, password, password2, disabled, result}) => {
  setViewer(store, genUser())
  wrapper = shallowMount(Credentials, {
    localVue,
    store,
    propsData: {username: 'Fox'},
    attachToDocument: true,
    sync: false,
  })
  const vm = wrapper.vm as any
  vm.passwordForm.fields.current_password.update(currentPassword)
  vm.passwordForm.fields.new_password.update(password)
  vm.passwordForm.fields.new_password2.update(password2)
  store.commit('forms/updateMeta', {name: 'passwordChange', meta: {disabled}})
  await vm.$nextTick()
  expect(vm.passwordDisabled).toBe(result)
})
  it('Hides all of the modals when the user is saved', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    const vm = wrapper.vm as any
    vm.showUsernameChange = true
    vm.showPasswordChange = true
    vm.showEmailChange = true
    await vm.$nextTick()
    expect(wrapper.findAll('.v-dialog--active').length).toBe(3)
    vm.save(genUser())
    await vm.$nextTick()
    expect(vm.showUsernameChange).toBe(false)
    expect(vm.showPasswordChange).toBe(false)
    expect(vm.showEmailChange).toBe(false)
    expect(wrapper.findAll('.v-dialog--active').length).toBe(0)
  })
})
