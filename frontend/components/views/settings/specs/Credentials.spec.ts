import {shallowMount, VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {Router, createRouter, createWebHistory} from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import Credentials from '../Credentials.vue'
import Settings from '../Settings.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

vi.useFakeTimers()

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
      name: 'Login Details',
      path: 'credentials',
      component: Credentials,
      props: true,
    },
  ],
}]

describe('Credentials.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let router: Router
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: settingRoutes,
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts the credentials page', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
  })
  test('Updates the url', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    expect(vm.url).toBe('/api/profiles/account/Fox/auth/credentials/')
    wrapper.setProps({username: 'Vulpes'})
    vm.subjectHandler.user.updateX({username: 'Vulpes'})
    await wrapper.vm.$nextTick()
    const newUrl = '/api/profiles/account/Vulpes/auth/credentials/'
    expect(vm.url).toBe(newUrl)
    expect(vm.usernameForm.endpoint).toBe(newUrl)
    expect(vm.passwordForm.endpoint).toBe(newUrl)
    expect(vm.emailForm.endpoint).toBe(newUrl)
  })
  test('Disables the email submit button if the current password is missing', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    vm.emailForm.fields.email.update('test@example.com')
    vm.emailForm.fields.email2.update('test@example.com')
    await vm.$nextTick()
    expect(vm.emailDisabled).toBe(true)
  })
  test.each`
    currentPassword   | email                 | email2                | disabled | result
    ${''}             | ${''}                 | ${'test@example.com'} | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${''}                 | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${true}  | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${false} | ${false}
  `('should set emailDisabled $result when email is $email and email2 is ' +
    '$email2 and current_password is $currentPassword and form disability ' +
    'is $disabled', async({
    currentPassword,
    email,
    email2,
    disabled,
    result,
  }) => {
    setViewer(store, genUser())
    wrapper = shallowMount(Credentials, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    vm.emailForm.fields.current_password.update(currentPassword)
    vm.emailForm.fields.email.update(email)
    vm.emailForm.fields.email2.update(email2)
    store.commit('forms/updateMeta', {
      name: 'emailChange',
      meta: {disabled},
    })
    await vm.$nextTick()
    expect(vm.emailDisabled).toBe(result)
  })
  test.each`
    currentPassword   | password              | password2             | disabled | result
    ${''}             | ${''}                 | ${'test@example.com'} | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${''}                 | ${false} | ${true}
    ${''}             | ${'test@example.com'} | ${'test@example2.com'}| ${false} | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example2.com'}| ${true}  | ${true}
    ${'test'}         | ${'test@example.com'} | ${'test@example.com'} | ${false} | ${false}
  `('should set emailDisabled $result when new_password is $password and new_password2 is ' +
    '$new_password2 and current_password is $currentPassword and form disability is $disabled',
    async({
      currentPassword,
      password,
      password2,
      disabled,
      result,
    }) => {
      setViewer(store, genUser())
      wrapper = shallowMount(Credentials, {
        ...vueSetup({store}),
        props: {username: 'Fox'},
      })
      const vm = wrapper.vm as any
      vm.passwordForm.fields.current_password.update(currentPassword)
      vm.passwordForm.fields.new_password.update(password)
      vm.passwordForm.fields.new_password2.update(password2)
      store.commit('forms/updateMeta', {
        name: 'passwordChange',
        meta: {disabled},
      })
      await vm.$nextTick()
      expect(vm.passwordDisabled).toBe(result)
    })
  test('Hides all the modals when the user is saved', async() => {
    setViewer(store, genUser())
    wrapper = mount(Credentials, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    vm.showUsernameChange = true
    vm.showPasswordChange = true
    vm.showEmailChange = true
    await vm.$nextTick()
    console.log(wrapper.html())
    expect(wrapper.findAll('.v-overlay--active').length).toBe(3)
    vm.save(genUser())
    await vm.$nextTick()
    expect(vm.showUsernameChange).toBe(false)
    expect(vm.showPasswordChange).toBe(false)
    expect(vm.showEmailChange).toBe(false)
    expect(wrapper.findAll('.v-overlay--active').length).toBe(0)
  })
})
