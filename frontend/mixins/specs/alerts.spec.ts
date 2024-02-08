import {mount} from '@vue/test-utils'
import AlertComponent from '@/specs/helpers/dummy_components/alert.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {AlertCategory} from '@/store/state.ts'
import {beforeEach, describe, expect, test, vi} from 'vitest'
import {vueSetup} from '@/specs/helpers/index.ts'

let store: ArtStore
const mockTrace = vi.spyOn(console, 'trace')
mockTrace.mockImplementation(() => undefined)

describe('Alerts mixin', () => {
  beforeEach(() => {
    store = createStore()
    mockTrace.mockClear()
  })
  test('Pushes an alert', async() => {
    const wrapper = mount(AlertComponent, vueSetup({store}));
    // noinspection TypeScriptValidateJSTypes
    (wrapper.vm as any).$alert({message: 'Stuff broke.', category: AlertCategory.INFO})
    expect(store.state.alerts[0].message).toBe('Stuff broke.')
    expect(store.state.alerts[0].category).toBe(AlertCategory.INFO)
    expect(store.state.alerts[0].timeout).toBe(7000)
  })
  test('Turns an Axios Error into useful alerts', async() => {
    const wrapper = mount(AlertComponent, vueSetup({store}))
    const func = (wrapper.vm as any).$errAlert('Stuff broke.')
    const spy = vi.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith({category: 'error', message: 'Stuff broke.'})
    expect(mockTrace).toHaveBeenCalledWith({})
    expect(store.state.alerts[0].message).toBe(
      'Stuff broke.',
    )
    expect(store.state.alerts[0].category).toBe(AlertCategory.ERROR)
    expect(store.state.alerts[0].timeout).toBe(7000)
  })
  test('Does not log to the console if told to ignore', async() => {
    const wrapper = mount(AlertComponent, vueSetup({store}))
    const func = (wrapper.vm as any).$errAlert('Stuff broke.')
    const spy = vi.spyOn((wrapper.vm as any), '$alert')
    func({}, true)
    expect(spy).toHaveBeenCalledWith({category: 'error', message: 'Stuff broke.'})
    expect(mockTrace).not.toHaveBeenCalled()
  })
  test('Turns an Axios Error into useful alerts with a default error message', async() => {
    const wrapper = mount(AlertComponent, vueSetup({store}))
    mockTrace.mockImplementationOnce(() => undefined)
    const func = (wrapper.vm as any).$errAlert()
    const spy = vi.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith(
      {category: 'error', message: 'We had an issue contacting the server. Please try again later!'},
    )
    expect(mockTrace).toHaveBeenCalledWith({})
  })
  test('Turns an Axios Error into useful alerts with a specified timeout', async() => {
    const wrapper = mount(AlertComponent, vueSetup({store}))
    const func = (wrapper.vm as any).$errAlert('Stuff broke', 1000)
    const spy = vi.spyOn((wrapper.vm as any), '$alert')
    func({})
    expect(spy).toHaveBeenCalledWith(
      {category: 'error', message: 'Stuff broke', timeout: 1000},
    )
    expect(mockTrace).toHaveBeenCalledWith({})
  })
})
