/* tslint:disable:max-line-length */
import mockAxios from '../../specs/helpers/mock-axios.ts'
import {
  artCall,
  clearMetaTag,
  crossDomain,
  csrfSafeMethod,
  deriveDisplayName,
  dotTraverse,
  extPreview,
  flatten,
  formatDate,
  formatDateTerse,
  formatDateTime,
  formatSize,
  getCookie,
  getExt,
  getHeaders,
  guestName,
  initDrawerValue,
  isImage,
  log,
  makeQueryParams,
  markRead,
  md,
  newUploadSchema,
  posse,
  ratings,
  ratingsNonExtreme,
  ratingsShortLister,
  setCookie,
  setMetaContent,
  singleQ,
  textualize,
  thumbFromSpec,
  truncateText,
  updateLinked,
} from '@/lib/lib.ts'
import {shallowMount, VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, flushPromises, mount, rq, rs, vueSetup} from '@/specs/helpers/index.ts'
import {LogLevels} from '@/types/LogLevels.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'

describe('artCall', () => {
  beforeEach(() => {
    mockAxios.reset()
    // Let's make sure we clear out any existing meta tags to isolate the tests better.
    document.querySelectorAll('meta').forEach((element) => element.remove())
  })
  test('Performs a GET request', () => {
    const catchFn = vi.fn()
    const thenFn = vi.fn()
    artCall({url: '/test/location/', method: 'get', data: {test: 'data'}}).then(thenFn).catch(catchFn)
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/test/location/',
      'get',
      {test: 'data'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    ))
    mockAxios.mockResponse({data: {successful: 'call'}})
    expect(thenFn).toHaveBeenCalledWith({successful: 'call'})
    expect(catchFn).not.toHaveBeenCalled()
  })
  test('Performs a POST request', () => {
    const catchFn = vi.fn()
    const thenFn = vi.fn()
    artCall({url: '/test/location2/', method: 'post', data: {test: 'data2'}}).then(thenFn).catch(catchFn)
    expect(mockAxios.request).toHaveBeenCalledWith(rq(
      '/test/location2/',
      'post',
      {test: 'data2'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}},
    ))
    mockAxios.mockResponse({data: {successful: 'call2'}})
    expect(thenFn).toHaveBeenCalledWith({successful: 'call2'})
    expect(catchFn).not.toHaveBeenCalled()
  })
  test('Calls a presuccess hook', () => {
    const preSuccess = vi.fn()
    artCall({url: '/test/location2/', method: 'post', data: {test: 'data2'}, preSuccess}).then()
    mockAxios.mockResponse({status: 205, data: {test: 'thing'}})
    expect(preSuccess).toHaveBeenCalledWith(
      {config: {}, data: {test: 'thing'}, headers: {}, status: 205, statusText: 'OK'},
    )
  })
})
describe('Filenname modifiers', () => {
  test.each`
    filename               | extension
    ${'test.exe'}          | ${'EXE'}
    ${'test@example.com'}  | ${'COM'}
    ${'test'}              | ${'TEST'}
    ${'test.JPG'}          | ${'JPG'}
  `('should derive the extension $extension from $filename.', ({filename, extension}) => {
    expect(getExt(filename)).toBe(extension)
  })
  test.each`
    filename               | result
    ${'test.exe'}          | ${false}
    ${'test@example.com'}  | ${false}
    ${'test'}              | ${false}
    ${''}                  | ${false}
    ${'test.jpg'}          | ${true}
    ${'test.jpEg'}         | ${true}
    ${'test.bmp'}          | ${true}
    ${'test.png'}          | ${true}
    ${'test.GIF'}          | ${true}
  `('should decide that file name $filename refers to an image is $result.',
    ({filename, result}) => {
      expect(isImage(filename)).toBe(result)
    })
  test.each`
    filename               | result
    ${'test'}              | ${'/static/icons/UN.KNOWN.png'}
    ${'test@example.com'}  | ${'/static/icons/UN.KNOWN.png'}
    ${'test.jpg'}          | ${'/static/icons/JPG.png'}
    ${''}                  | ${'/static/icons/UN.KNOWN.png'}
    ${'test.jpEg'}         | ${'/static/icons/JPEG.png'}
    ${'test.doc'}          | ${'/static/icons/DOC.png'}
  `('should should produce the correct extension preview path for $filename.',
    ({filename, result}) => {
      expect(extPreview(filename)).toBe(result)
    })
  test.each`
    markdown               | text
    ${'test'}              | ${'test'}
    ${'**test**'}          | ${'test'}
    ${'# test thing here'} | ${'test thing here'}
    ${''}                  | ${''}
    ${'1. First'}          | ${'First'}
  `('should reduce $markdown to $text.',
    ({markdown, text}) => {
      expect(textualize(markdown)).toBe(text)
    })
})
describe('Meta tag managers', () => {
  test('Sets arbitrary meta tags', () => {
    // I don't know if this is properly isolated
    expect(document.head.querySelector('meta[name=test]')).toBeFalsy()
    setMetaContent('test', 'example')
    const meta = document.head.querySelector('meta[name=test]')
    expect(meta as Element).toBeTruthy()
    expect((meta as Element).textContent).toBe('example')
  })
  test('Replaces existing tags', () => {
    setMetaContent('test', 'example')
    setMetaContent('test', 'example2')
    const elements = document.querySelectorAll('meta')
    expect(elements.length).toBe(1)
    const meta = elements[0]
    expect(meta.textContent).toBe('example2')
  })
  test('Sets tags with arbitrary properties', () => {
    setMetaContent('test', 'example', {content: 'Stuff'})
    const element = document.querySelector('meta')
    expect(element).toBeTruthy()
    expect((element as Element).getAttribute('content')).toBe('Stuff')
  })
  test('Clears arbitrary meta tags', () => {
    const desctag = document.createElement('meta')
    desctag.setAttribute('name', 'test2')
    document.head.appendChild(desctag)
    expect(document.head.querySelector('meta[name=test2]')).toBeTruthy()
    clearMetaTag('test2')
    expect(document.head.querySelector('meta[name=test2]')).toBeFalsy()
  })
  test('Does not break if trying to clear a meta tag which does not exist', () => {
    document.createElement('meta')
    clearMetaTag('test2')
  })
})
describe('Enumerators', () => {
  let wrapper: VueWrapper<any>
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    // @ts-ignore
    delete window.PRERENDERING
  })
  test('Generates shortened options for ratings', () => {
    expect(ratingsShortLister()).toEqual(
      [
        {text: 'Clean/Safe', value: '0'}, {text: 'Risque', value: '1'},
        {text: 'Adult content', value: '2'},
        {text: 'Offensive/Disturbing', value: '3'},
      ],
    )
  })
  test('Generates a set of rating options', () => {
    expect(ratings()).toEqual([
      {text: 'Clean/Safe for work', value: '0'},
      {text: 'Risque/mature, not adult content but not safe for work', value: '1'},
      {text: 'Adult content, not safe for work', value: '2'},
      {text: 'Offensive/Disturbing to most viewers, not safe for work', value: '3'},
    ])
  })
  test('Generates a redacted set of rating options', () => {
    expect(ratingsNonExtreme()).toEqual([
      {text: 'Clean/Safe for work', value: '0'},
      {text: 'Risque/mature, not adult content but not safe for work', value: '1'},
      {text: 'Adult content, not safe for work', value: '2'},
    ])
  })
  test('Generates a standard schema for submission upload', () => {
    wrapper = shallowMount(Empty, vueSetup({store}))
    const handler = wrapper.vm.$getProfile('person', {})
    expect(newUploadSchema(handler.user)).toEqual({
      endpoint: '/api/profiles/account/person/submissions/',
      reset: false,
      fields: {
        title: {value: '', step: 2},
        caption: {value: '', step: 2},
        private: {value: false, step: 2},
        comments_disabled: {value: false, step: 2},
        rating: {value: 0, step: 1},
        file: {value: '', step: 1},
        preview: {value: '', step: 1},
        tags: {value: [], step: 1},
        characters: {value: [], step: 1},
        artists: {value: [], step: 1},
      },
    })
  })
})
describe('HTTP Helpers', () => {
  test('Constructs the appropriate headers for a POST request', () => {
    setCookie('csrftoken', 'Stuff')
    setCookie('referredBy', 'Jimmy')
    window.windowId = 'Blabla'
    expect(getHeaders('post', '/test/')).toEqual(
      {
        'Content-Type': 'application/json; charset=utf-8',
        'X-CSRFToken': 'Stuff',
        'X-Referred-By': 'Jimmy',
        'X-Window-ID': 'Blabla',
      },
    )
  })
  test('Constructs the appropriate headers for an outside POST request', () => {
    setCookie('csrftoken', 'Stuff')
    expect(getHeaders('post', 'https://example.com/')).toEqual(
      {'Content-Type': 'application/json; charset=utf-8'},
    )
  })
  test('Constructs the appropriate headers for a GET request', () => {
    setCookie('csrftoken', 'Stuff')
    expect(getHeaders('get', '/test/')).toEqual(
      {'Content-Type': 'application/json; charset=utf-8'},
    )
  })
  test.each`
    url                      | result
    ${'https://example.com/'}| ${true}
    ${'//test.com/thing'}    | ${true}
    ${String(window.location)}       | ${false}
    ${'/'}                   | ${false}
  `('should determine the cross-domain status of $url to be $result.',
    ({url, result}) => {
      expect(crossDomain(url)).toEqual(result)
    })
  test.each`
    method       | result
    ${'get'}     | ${true}
    ${'GET'}     | ${true}
    ${'POST'}    | ${false}
    ${'PUT'}     | ${false}
    ${'OPTions'} | ${true}
    ${'Head'}    | ${true}
    ${'trace'}   | ${true}
    ${'deLEte'}  | ${false}
    ${'unknown'} | ${false}
  `('Should determine the CSRF safety of method $method to be $result', ({method, result}) => {
    expect(csrfSafeMethod(method)).toBe(result)
  })
  test('Sets a cookie', () => {
    setCookie('test', 'value')
    expect(getCookie('test')).toBe('value')
  })
  test('Sets a cookie with an expiration date', () => {
    setCookie('test', 'value', 1)
    // We can't actually check if the date was set correctly, just that coverage said the appropriate code ran.
    expect(getCookie('test')).toBe('value')
  })
})
describe('Formatters', () => {
  test('Formats a datetime string', () => {
    expect(formatDateTime('2019-05-03T15:41:36.902Z')).toBe('May 3rd 2019, 10:41:36 am')
  })
  test('Formats a date string', () => {
    expect(formatDate('2019-05-03')).toBe('May 3rd 2019')
  })
  test('Formats a date string, tersely', () => {
    expect(formatDateTerse(new Date().getFullYear() + '-05-03')).toBe('May 3rd')
  })
  test('Falls back to full year display if asked to be terse but the year is different', () => {
    expect(formatDateTerse('2019-05-03')).toBe('May 3rd 19')
  })
  test('Formats a datetime string as a date', () => {
    expect(formatDate('2019-05-03T15:41:36.902Z')).toBe('May 3rd 2019')
  })
  test('Does not truncate text that is under the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 50)).toBe(
      'This is a test string. It is 49 characters long.',
    )
  })
  test('Truncates text that is over the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 4)).toBe('This...')
  })
  test('Truncates before the space when over the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 5)).toBe('This...')
  })
  test('Does not truncate text mid-word if it can be avoided', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 12)).toBe(
      'This is a...',
    )
  })
  test('Truncates mid-word if it has no other choice', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 2)).toBe(
      'Th...',
    )
  })
  test.each`
    size             | result
    ${1000}          | ${'1000 B'}
    ${10000}         | ${'9.77 KB'}
    ${10000000}      | ${'9.54 MB'}
    ${10000000000}   | ${'9.31 GB'}
    ${10000000000000}| ${'9.09 TB'}
  `('Makes the byte size $size human readable as $result', ({size, result}) => {
    expect(formatSize(size)).toBe(result)
  })
  test('Renders markdown with links', () => {
    expect(md.render(`# Hello there.

*This is a test of the markdown renderer.* **There is no need to be alarmed.**
<a href='https://example.com/'>I'm going to try a manual link.</a>

[Here's a markdown link](http://example.com/)

[Here's another markdown link](/)

Here's a raw link: https://example.com/

Here's an email: support@artconomy.com`)).toBe(`<h1>Hello there.</h1>
<p><em>This is a test of the markdown renderer.</em> <strong>There is no need to be alarmed.</strong><br>
&lt;a href='<a href="https://example.com/'%3EI'm" target="_blank" rel="nofollow noopener">https://example.com/'&gt;I'm</a> going to try a manual link.&lt;/a&gt;</p>
<p><a href="http://example.com/" target="_blank" rel="nofollow noopener">Here's a markdown link</a></p>
<p><a href="/" target="_blank" onclick="artconomy.$router.history.push('/');return false">Here's another markdown link</a></p>
<p>Here's a raw link: <a href="https://example.com/" target="_blank" rel="nofollow noopener">https://example.com/</a></p>
<p>Here's an email: <a href="mailto:support@artconomy.com" target="_blank">support@artconomy.com</a></p>
`)
  })
  test('Does not render links if prerender is set to true', () => {
    window.PRERENDERING = 1
    expect(md.render(`# Hello there.

*This is a test of the markdown renderer.* **There is no need to be alarmed.**
<a href='https://example.com/'>I'm going to try a manual link.</a>

[Here's a markdown link](http://example.com/)

[Here's another markdown link](/)

Here's a raw link: https://example.com/

Here's an email: support@artconomy.com`)).toBe(`<h1>Hello there.</h1>
<p><em>This is a test of the markdown renderer.</em> <strong>There is no need to be alarmed.</strong><br>
&lt;a href='https://example.com/'&gt;I'm going to try a manual link.&lt;/a&gt;</p>
<p>Here's a markdown link</p>
<p>Here's another markdown link</p>
<p>Here's a raw link: https://example.com/</p>
<p>Here's an email: support@artconomy.com</p>
`)
  })
  test('Renders markdown with Mentions', () => {
    expect(md.render(
      'Hello, @Foxie. Is this @Vulpine creature as \\@sweet and cu@te @ as I\'d hope? Maybe @Fox\'s tricks ' +
      'will tell us.')).toBe(
      '<p>Hello, <a href="/profile/Foxie/about" onclick="artconomy.$router.push(\'/profile/Foxie/about\');return false">@Foxie</a>.' +
      ' Is this <a href="/profile/Vulpine/about" onclick="artconomy.$router.push(\'/profile/Vulpine/about\');return false">@Vulpine</a> creature ' +
      'as @sweet and cu@te @ as I\'d hope? Maybe <a href="/profile/Fox/about" onclick="artconomy.$router.push(\'/profile/Fox/about\');return false">@Fox</a>\'s ' +
      `tricks will tell us.</p>
`)
  })
  test.each`
    input                           | result
    ${'lists'}                      | ${'lists'}
    ${'lists/thing'}                | ${'lists_thing'}
    ${'stuff.wut'}                  | ${'stuff_wut'}
    ${'this.thing/is/quite.nested'} | ${'this_thing_is_quite_nested'}
    ${'this_has_underscores'}       | ${'this__has__underscores'}
  `('Should flatten $input into $result', ({input, result}) => {
    expect(flatten(input)).toBe(result)
  })
  test.each`
  userList                       | additional    | result
  ${['user1', 'user2', 'user3']} | ${0}          | ${'user1, user2, and user3'}
  ${['user1', 'user2', 'user3']} | ${3}          | ${'user1, user2, user3 and 3 others'}
  ${['user1', 'user2', 'user3']} | ${1}          | ${'user1, user2, user3 and 1 other'}
  ${['user1', 'user2']}          | ${0}          | ${'user1 and user2'}
  ${['user1']}                   | ${0}          | ${'user1'}
  `('Should format a posse', ({userList, additional, result}) => {
    expect(posse(userList, additional)).toEqual(result)
  })
  test.each`
  userName         | result
  ${'_'}           | ${''}
  ${'__4'}         | ${'Guest #4'}
  ${'Fox'}         | ${'Fox'}
  ${null}          | ${''}
  ${'__deleted45'} | ${'[deleted]'}
  `('Should format a display name based on a username', ({userName, result}) => {
    expect(deriveDisplayName(userName)).toBe(result)
  })
  test.each`
  userName       | result
  ${'Guest #5'}  | ${true}
  ${'__5'}       | ${true}
  ${'Fox'}       | ${false}
  `('Can determine whether a username belongs to a guest account', ({userName, result}) => {
    expect(guestName(userName)).toBe(result)
  })
})

describe('Path helpers', () => {
  test.each`
    paramSet             | result
    ${'test'}            | ${'test'}
    ${['test', 'test2']} | ${'test'}
    ${[]}                | ${''}
    ${[null]}            | ${''}
    ${null}              | ${''}
  `('Should derive $result from query param set $paramSet', ({paramSet, result}) => {
    expect(singleQ(paramSet)).toBe(result)
  })
})

describe('dotTraverse', () => {
  const item = {
    thing: {
      stuff: {
        wat: 'Yay',
      },
      erp: 'Nope',
    },
  }
  test('Traverses a tree to find a particular result and an end branch', () => {
    expect(dotTraverse(item, 'thing.stuff.wat')).toBe('Yay')
  })
  test('Traverses a tree to find a result mid-branch', () => {
    expect(dotTraverse(item, 'thing.stuff')).toEqual({wat: 'Yay'})
  })
  test('Raises an exception if the path does not exist', () => {
    expect(() => dotTraverse(item, 'thing.stuff.org.wat')).toThrow(
      Error('Property thing.stuff.org is not defined.'),
    )
  })
  test('Returns undefined if silenced and the path does not exist', () => {
    expect(dotTraverse(item, 'thing.stuff.org.wat', true)).toBe(undefined)
  })
})

describe('thumbFromSpec', () => {
  test('Returns the full image by default if the thumbnail is not present', () => {
    const file = {full: '/thing/wat.jpg', type: 'data:image'}
    expect(thumbFromSpec('thumbnail', file)).toBe('/thing/wat.jpg')
  })
  test('Returns the correct thumbnail', () => {
    const file = {full: '/thing/wat.jpg', thumbnail: '/stuff/things.jpg', type: 'data:image'}
    expect(thumbFromSpec('thumbnail', file)).toBe('/stuff/things.jpg')
  })
})

describe('makeQueryParams', () => {
  test('Wat', () => {
    const testData = {stuff: false, things: true, wat: 2}
    expect(makeQueryParams(testData)).toEqual({stuff: 'false', things: 'true', wat: '2'})
  })
})

describe('Mark Read handler', () => {
  beforeEach(() => {
    mockAxios.reset()
  })
  afterEach(() => {
    cleanUp()
  })
  test('Marks an item as read', async() => {
    const target = mount(Empty, vueSetup()).vm.$getSingle(
      'boop', {endpoint: '/test/', x: {id: 1, read: false}},
    )
    markRead(target, 'stuff.Things')
    const req = mockAxios.lastReqGet()
    expect(req.url).toBe('/api/lib/read-marker/stuff.Things/1/')
    expect(req.method).toBe('post')
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect(target.x.read).toBe(true)
  })
  test('Bails early if the object is null', () => {
    const target = mount(Empty, vueSetup()).vm.$getSingle(
      'boop', {endpoint: '/test/', x: null},
    )
    markRead(target, 'stuff.Things')
    expect(mockAxios.lastReqGet()).toBe(undefined)
  })
  test('Bails early if the object has already been read', () => {
    const target = mount(Empty, vueSetup()).vm.$getSingle(
      'boop', {endpoint: '/test/', x: {id: 1, read: true}},
    )
    markRead(target, 'stuff.Things')
    expect(mockAxios.lastReqGet()).toBe(undefined)
  })
})

declare type TestType = {id: number, thing: {id: number, read: boolean}}

describe('Linked update handler', () => {
  test('Updates a list with linked references', () => {
    const targetList = mount(Empty, vueSetup()).vm.$getList(
      'boop', {endpoint: '/test/'},
    )
    targetList.setList([
      {id: 1, thing: {id: 2, read: false}},
      {id: 2, thing: {id: 4, read: false}},
      {id: 3, thing: {id: 1, read: false}},
    ])
    updateLinked({list: targetList, newValue: {id: 2, read: true}, key: 'thing'})
    expect(targetList.list.map((x: SingleController<TestType>) => x.x)).toEqual([
      {id: 1, thing: {id: 2, read: true}},
      {id: 2, thing: {id: 4, read: false}},
      {id: 3, thing: {id: 1, read: false}},
    ])
  })
  test('Handles a subKey', () => {
    const targetList = mount(Empty, vueSetup()).vm.$getList(
      'boop', {endpoint: '/test/'},
    )
    targetList.setList([
      {id: 1, thing: {stuff: 2, read: false}},
      {id: 2, thing: {stuff: 4, read: false}},
      {id: 3, thing: {stuff: 1, read: false}},
    ])
    updateLinked({list: targetList, newValue: {stuff: 2, read: true}, key: 'thing', subKey: 'stuff'})
    expect(targetList.list.map((x: SingleController<TestType>) => x.x)).toEqual([
      {id: 1, thing: {stuff: 2, read: true}},
      {id: 2, thing: {stuff: 4, read: false}},
      {id: 3, thing: {stuff: 1, read: false}},
    ])
  })
  test('Bails early if the value is null', () => {
    const targetList = mount(Empty, vueSetup()).vm.$getList(
      'boop', {endpoint: '/test/'},
    )
    targetList.setList([
      {id: 1, thing: {id: 2, read: false}},
      {id: 2, thing: {id: 4, read: false}},
      {id: 3, thing: {id: 1, read: false}},
    ])
    updateLinked({list: targetList, newValue: null, key: 'thing'})
    expect(targetList.list.map((x: SingleController<TestType>) => x.x)).toEqual([
      {id: 1, thing: {id: 2, read: false}},
      {id: 2, thing: {id: 4, read: false}},
      {id: 3, thing: {id: 1, read: false}},
    ])
  })
})

describe('Logger', () => {
  const debug = vi.spyOn(console, 'debug')
  debug.mockImplementation(() => undefined)
  const info = vi.spyOn(console, 'info')
  info.mockImplementation(() => undefined)
  const warn = vi.spyOn(console, 'warn')
  warn.mockImplementation(() => undefined)
  const error = vi.spyOn(console, 'error')
  error.mockImplementation(() => undefined)
  beforeEach(() => {
    debug.mockReset()
    info.mockReset()
    warn.mockReset()
    error.mockReset()
  })
  const sendMessages = () => {
    log.debug('TestDebug')
    log.info('TestInfo')
    log.warn('TestWarn')
    log.error('TestError')
  }
  test('Sends only errors', () => {
    window.__LOG_LEVEL__ = LogLevels.ERROR
    sendMessages()
    expect(debug).not.toHaveBeenCalled()
    expect(info).not.toHaveBeenCalled()
    expect(warn).not.toHaveBeenCalled()
    expect(error).toHaveBeenCalledWith('TestError')
    expect(error).toHaveBeenCalledTimes(1)
  })
  test('Sends warnings and up', () => {
    window.__LOG_LEVEL__ = LogLevels.WARN
    sendMessages()
    expect(debug).not.toHaveBeenCalled()
    expect(info).not.toHaveBeenCalled()
    expect(warn).toHaveBeenCalledWith('TestWarn')
    expect(warn).toHaveBeenCalledTimes(1)
    expect(error).toHaveBeenCalledWith('TestError')
    expect(error).toHaveBeenCalledTimes(1)
  })
  test('Sends info and up', () => {
    window.__LOG_LEVEL__ = LogLevels.INFO
    sendMessages()
    expect(debug).not.toHaveBeenCalled()
    expect(info).toHaveBeenCalledWith('TestInfo')
    expect(info).toHaveBeenCalledTimes(1)
    expect(warn).toHaveBeenCalledWith('TestWarn')
    expect(warn).toHaveBeenCalledTimes(1)
    expect(error).toHaveBeenCalledWith('TestError')
    expect(error).toHaveBeenCalledTimes(1)
  })
  test('Sends all logging levels', () => {
    window.__LOG_LEVEL__ = LogLevels.DEBUG
    sendMessages()
    expect(debug).toHaveBeenCalledWith('TestDebug')
    expect(debug).toHaveBeenCalledTimes(1)
    expect(info).toHaveBeenCalledWith('TestInfo')
    expect(info).toHaveBeenCalledTimes(1)
    expect(warn).toHaveBeenCalledWith('TestWarn')
    expect(warn).toHaveBeenCalledTimes(1)
    expect(error).toHaveBeenCalledWith('TestError')
    expect(error).toHaveBeenCalledTimes(1)
  })
  test('Sends all logging levels if the log level is super high', () => {
    window.__LOG_LEVEL__ = LogLevels.ERROR + 1
    sendMessages()
    expect(debug).not.toHaveBeenCalled()
    expect(info).not.toHaveBeenCalled()
    expect(warn).not.toHaveBeenCalled()
    expect(debug).not.toHaveBeenCalled()
  })
})

describe('initDrawerValue', () => {
  test('Handles a blank initial value', () => {
    expect(initDrawerValue()).toBe(null)
  })
  test('Handles a set initial value', () => {
    localStorage.setItem('drawerOpen', 'true')
    expect(initDrawerValue()).toBe(true)
  })
})
