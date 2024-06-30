import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {describe, expect, test} from 'vitest'
import {deriveImage} from '@/plugins/shortcuts.ts'
import {Ratings} from '@/types/Ratings.ts'


describe('shortcuts.ts', () => {
  test('Handles a null asset', async() => {
    expect(deriveImage(null, 'preview', true, Ratings.ADULT)).toBe('/static/images/default-avatar.png')
  })
  test('Handles a submission with a viewable rating', async() => {
    const submission = genSubmission()
    submission.rating = Ratings.ADULT
    expect(deriveImage(submission, 'thumbnail', true, Ratings.ADULT)).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
    )
    expect(deriveImage(submission, 'blabla', false, Ratings.ADULT)).toBe(undefined)
  })
  test('Handles a submission with an unviewable rating', async() => {
    const adultSubmission = genSubmission()
    adultSubmission.rating = 3
    expect(deriveImage(adultSubmission, 'thumbnail', true, Ratings.ADULT)).toBe(
      '/static/images/default-avatar.png',
    )
    expect(deriveImage(adultSubmission, 'thumbnail', false, Ratings.ADULT)).toBe(
      '',
    )
  })
  test('Handles a submission with a preview', async() => {
    const submission = genSubmission()
    submission.preview = {
      thumbnail: '/test/image.png',
    }
    expect(deriveImage(submission, 'thumbnail', true, Ratings.ADULT)).toBe(
      '/test/image.png',
    )
    expect(deriveImage(submission, 'gallery', false, Ratings.ADULT)).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.1000x700_q85.png',
    )
  })
  test('Handles an SVG', async() => {
    const submission = genSubmission()
    submission.file.full = '/test/image.svg'
    expect(deriveImage(submission, 'thumbnail', true, Ratings.ADULT)).toBe(
      '/test/image.svg',
    )
  })
  test('Handles a non-image file thumbnail', async() => {
    const submission = genSubmission()
    submission.file.full = '/test/image.mp4'
    expect(deriveImage(submission, 'thumbnail', true, Ratings.ADULT)).toBe(
      '/static/icons/MP4.png',
    )
  })
})
