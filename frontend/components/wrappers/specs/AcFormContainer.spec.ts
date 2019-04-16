import {createLocalVue, mount} from '@vue/test-utils'
import FormContainer from '@/specs/helpers/dummy_components/form-container.vue'
import {AxiosError} from 'axios'
import {FormControllers} from '@/store/forms/registry'
import Vuetify from 'vuetify'
import {vuetifySetup} from '@/specs/helpers'
import Vue from 'vue'
import Vuex from 'vuex'
import {ArtStore, createStore} from '@/store'

const mockTrace = jest.spyOn(console, 'trace')

Vue.use(Vuetify)
Vue.use(Vuex)
const localVue = createLocalVue()
localVue.use(FormControllers)

describe('ac-form-container.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
    vuetifySetup()
  })
  it('Sets default properties', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(FormContainer, {
      localVue, store,
    })
    expect((wrapper.vm as any).$refs.defaultForm.errors).toEqual([])
    expect((wrapper.vm as any).$refs.defaultForm.sending).toEqual(false)
  })
  it('Displays dismissable errors', async() => {
    const wrapper = mount(FormContainer, {
      localVue, store,
    })
    const vm = wrapper.vm as any
    mockTrace.mockImplementationOnce(() => undefined)
    vm.basicForm.setErrors({} as AxiosError)
    await vm.$nextTick()
    wrapper.find('.v-alert__dismissible').trigger('click')
    await vm.$nextTick()
  })
})
