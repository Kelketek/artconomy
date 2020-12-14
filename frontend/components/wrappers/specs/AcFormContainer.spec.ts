import {mount} from '@vue/test-utils'
import FormContainer from '@/specs/helpers/dummy_components/form-container.vue'
import {AxiosError} from 'axios'
import {createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import Vuetify from 'vuetify/lib'

const mockTrace = jest.spyOn(console, 'trace')

const localVue = vueSetup()
let vuetify: Vuetify

describe('ac-form-container.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    vuetify = createVuetify()
    store = createStore()
  })
  it('Sets default properties', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(FormContainer, {
      localVue,
      store,
      vuetify,
    })
    expect((wrapper.vm as any).$refs.defaultForm.errors).toEqual([])
    expect((wrapper.vm as any).$refs.defaultForm.sending).toEqual(false)
  })
  it('Displays dismissible errors', async() => {
    const wrapper = mount(FormContainer, {
      localVue,
      store,
      vuetify,
    })
    const vm = wrapper.vm as any
    mockTrace.mockImplementationOnce(() => undefined)
    vm.basicForm.setErrors({} as AxiosError)
    await vm.$nextTick()
    wrapper.find('.v-alert__dismissible').trigger('click')
    await vm.$nextTick()
  })
})
