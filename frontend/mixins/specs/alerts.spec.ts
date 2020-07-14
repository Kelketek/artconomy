import {createLocalVue, mount} from '@vue/test-utils'
import AlertComponent from '@/specs/helpers/dummy_components/alert.vue'
import {ArtStore, createStore} from '@/store'
import Vuex from 'vuex'
import {AlertCategory} from '@/store/state'

const localVue = createLocalVue()
localVue.use(Vuex)
let store: ArtStore
const mockTrace = jest.spyOn(console, 'trace')
mockTrace.mockImplementation(() => undefined)

describe('Alerts mixin', () => {
  beforeEach(() => {
    store = createStore()
    mockTrace.mockClear()
  })
  it('Pushes an alert', async() => {
    const wrapper = mount(AlertComponent, {localVue, store});
    // noinspection TypeScriptValidateJSTypes
    (wrapper.vm as any).$alert({message: 'Stuff broke.', category: AlertCategory.INFO})
    expect(store.state.alerts[0].message).toBe('Stuff broke.')
    expect(store.state.alerts[0].category).toBe(AlertCategory.INFO)
    expect(store.state.alerts[0].timeout).toBe(7000)
  })
  it('Turns an Axios Error into useful alerts', async() => {
    const wrapper = mount(AlertComponent, {localVue, store})
    const func = (wrapper.vm as any).$errAlert('Stuff broke.')
    const spy = jest.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith({category: 'error', message: 'Stuff broke.'})
    expect(mockTrace).toHaveBeenCalledWith({})
    expect(store.state.alerts[0].message).toBe(
      'Stuff broke.',
    )
    expect(store.state.alerts[0].category).toBe(AlertCategory.ERROR)
    expect(store.state.alerts[0].timeout).toBe(7000)
  })
  it('Does not log to the console if told to ignore', async() => {
    const wrapper = mount(AlertComponent, {localVue, store})
    const func = (wrapper.vm as any).$errAlert('Stuff broke.')
    const spy = jest.spyOn((wrapper.vm as any), '$alert')
    func({}, true)
    expect(spy).toHaveBeenCalledWith({category: 'error', message: 'Stuff broke.'})
    expect(mockTrace).not.toHaveBeenCalled()
  })
  it('Turns an Axios Error into useful alerts with a default error message', async() => {
    const wrapper = mount(AlertComponent, {localVue, store})
    mockTrace.mockImplementationOnce(() => undefined)
    const func = (wrapper.vm as any).$errAlert()
    const spy = jest.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith(
      {category: 'error', message: 'We had an issue contacting the server. Please try again later!'},
    )
    expect(mockTrace).toHaveBeenCalledWith({})
  })
  it('Turns an Axios Error into useful alerts with a specified timeout', async() => {
    const wrapper = mount(AlertComponent, {localVue, store})
    const func = (wrapper.vm as any).$errAlert('Stuff broke', 1000)
    const spy = jest.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith(
      {category: 'error', message: 'Stuff broke', timeout: 1000},
    )
    expect(mockTrace).toHaveBeenCalledWith({})
  })
})
