import {expect, vi, it, describe, beforeEach} from 'vitest'
import {waitFor} from '@/specs/helpers'
import QrCode from '@/components/wrappers/QrCode.ts'
import {render} from '@testing-library/vue'

const qrImageUrl = 'otpauth://totp/Artconomy%20Dev%3Afox%40vulpinity.com?secret=KJZWLZLDMVY3XJAX72V4WAXDKKZZDA76' +
  '&algorithm=SHA1&digits=6&period=30&issuer=Artconomy+Dev'

describe('QrCode.ts', () => {
  const mockError = vi.spyOn(console, 'error')
  beforeEach(() => {
    mockError.mockReset()
  })
  it('Logs an error if there was an issue building the QR code image', async () => {
    mockError.mockImplementationOnce(() => undefined)
    render(QrCode, {props: {data: ''}})
    await waitFor(() => expect(mockError).toHaveBeenCalledWith(Error('No input text')))
  })
  it('Displays a QR code', async () => {
    const wrapper = render(QrCode, {props: {data: qrImageUrl}})
    await waitFor(() => expect(wrapper.html()).toContain('█▀▀▀▀▀█'))
  })
})
