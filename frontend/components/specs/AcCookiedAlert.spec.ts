import AcCookiedAlert from '@/components/AcCookiedAlert.vue'
import {render, fireEvent, RenderResult} from '@testing-library/vue'
import {beforeEach, afterEach, describe, expect, it} from 'vitest'
import {deleteCookie, getCookie} from '@/lib/lib.ts'
import {cleanUp, vueSetup, waitFor} from '@/specs/helpers'

let wrapper: RenderResult

describe('AcCookiedAlert.vue', () => {
  beforeEach(() => {
    deleteCookie('boop')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Displays an alert when there is no cookie.', async () => {
    const wrapper = render(AcCookiedAlert, {...vueSetup(), slots: {default: 'This is test text.'}, props: {cookie: 'boop'}})
    wrapper.getByText('This is test text.')
    const closeButton = wrapper.getByRole('button')
    await fireEvent.click(closeButton)
    await waitFor(() => expect(wrapper.html()).toEqual(''))
    expect(getCookie('boop')).toBe('read')
  })
})
