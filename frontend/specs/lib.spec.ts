/* tslint:disable:max-line-length */
import mockAxios from './helpers/mock-axios'
import moment from 'moment-timezone'
import {
  artCall,
  clearMetaTag,
  crossDomain,
  csrfSafeMethod, deriveDisplayName, dotTraverse,
  extPreview, flatten,
  formatDate,
  formatDateTime, formatSize,
  getCookie,
  getExt,
  getHeaders, guestName,
  isImage, makeQueryParams,
  md, newUploadSchema, posse,
  ratings,
  ratingsNonExtreme,
  ratingsShort,
  setCookie,
  setMetaContent,
  singleQ,
  textualize, thumbFromSpec, truncateText,
} from '@/lib'
import VueRouter from 'vue-router'
import {createLocalVue, mount, shallowMount, Wrapper} from '@vue/test-utils'
import ParamTabbed from '@/specs/helpers/dummy_components/param-tabbed.vue'
import Routed from '@/specs/helpers/dummy_components/routed.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {Singles} from '@/store/singles/registry'
import {Lists} from '@/store/lists/registry'
import {Profiles} from '@/store/profiles/registry'
import {ArtStore, createStore} from '@/store'

Vue.use(Vuetify)
Vue.use(Vuex)

describe('artCall', () => {
  beforeEach(() => {
    mockAxios.reset()
    // Let's make sure we clear out any existing meta tags to isolate the tests better.
    document.querySelectorAll('meta').forEach((element) => element.remove())
  })
  afterEach(() => {
    moment.tz.setDefault()
  })
  it('Performs a GET request', () => {
    const catchFn = jest.fn()
    const thenFn = jest.fn()
    artCall({url: '/test/location/', method: 'get', data: {test: 'data'}}).then(thenFn).catch(catchFn)
    expect(mockAxios.get).toHaveBeenCalledWith(
      '/test/location/',
      {test: 'data'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}}
    )
    mockAxios.mockResponse({data: {successful: 'call'}})
    expect(thenFn).toHaveBeenCalledWith({successful: 'call'})
    expect(catchFn).not.toHaveBeenCalled()
  })
  it('Performs a POST request', () => {
    const catchFn = jest.fn()
    const thenFn = jest.fn()
    artCall({url: '/test/location2/', method: 'post', data: {test: 'data2'}}).then(thenFn).catch(catchFn)
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/test/location2/',
      {test: 'data2'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}}
    )
    mockAxios.mockResponse({data: {successful: 'call2'}})
    expect(thenFn).toHaveBeenCalledWith({successful: 'call2'})
    expect(catchFn).not.toHaveBeenCalled()
  })
  it('Calls a presuccess hook', () => {
    const preSuccess = jest.fn()
    artCall({url: '/test/location2/', method: 'post', data: {test: 'data2'}, preSuccess}).then()
    mockAxios.mockResponse({status: 205, data: {test: 'thing'}})
    expect(preSuccess).toHaveBeenCalledWith(
      {config: {}, data: {test: 'thing'}, headers: {}, status: 205, statusText: 'OK'}
    )
  })
})
describe('Filenname modifiers', () => {
  it.each`
    filename               | extension
    ${'test.exe'}          | ${'EXE'}
    ${'test@example.com'}  | ${'COM'}
    ${'test'}              | ${'TEST'}
    ${'test.JPG'}          | ${'JPG'}
  `('should derive the extension $extension from $filename.', ({filename, extension}) => {
  expect(getExt(filename)).toBe(extension)
})
  it.each`
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
  it.each`
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
  it.each`
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
  it('Sets arbitrary meta tags', () => {
    // I don't know if this is properly isolated
    expect(document.head.querySelector('meta[name=test]')).toBeFalsy()
    setMetaContent('test', 'example')
    const meta = document.head.querySelector('meta[name=test]')
    expect(meta as Element).toBeTruthy()
    expect((meta as Element).textContent).toBe('example')
  })
  it('Replaces existing tags', () => {
    setMetaContent('test', 'example')
    setMetaContent('test', 'example2')
    const elements = document.querySelectorAll('meta')
    expect(elements.length).toBe(1)
    const meta = elements[0]
    expect(meta.textContent).toBe('example2')
  })
  it('Sets tags with arbitrary properties', () => {
    setMetaContent('test', 'example', {content: 'Stuff'})
    const element = document.querySelector('meta')
    expect(element).toBeTruthy()
    expect((element as Element).getAttribute('content')).toBe('Stuff')
  })
  it('Clears arbitrary meta tags', () => {
    const desctag = document.createElement('meta')
    desctag.setAttribute('name', 'test2')
    document.head.appendChild(desctag)
    expect(document.head.querySelector('meta[name=test2]')).toBeTruthy()
    clearMetaTag('test2')
    expect(document.head.querySelector('meta[name=test2]')).toBeFalsy()
  })
  it('Does not break if trying to clear a meta tag which does not exist', () => {
    document.createElement('meta')
    clearMetaTag('test2')
  })
})
describe('Enumerators', () => {
  const localVue = createLocalVue()
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  localVue.use(Singles)
  localVue.use(Lists)
  localVue.use(Profiles)
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    delete window.PRERENDERING
  })
  it('Generates shortened options for ratings', () => {
    expect(ratingsShort()).toEqual(
      [
        {text: 'Clean/Safe', value: '0'}, {text: 'Risque', value: '1'},
        {text: 'Adult content', value: '2'},
        {text: 'Offensive/Disturbing', value: '3'},
      ]
    )
  })
  it('Generates a set of rating options', () => {
    expect(ratings()).toEqual([
      {text: 'Clean/Safe for work', value: '0'},
      {text: 'Risque/mature, not adult content but not safe for work', value: '1'},
      {text: 'Adult content, not safe for work', value: '2'},
      {text: 'Offensive/Disturbing to most viewers, not safe for work', value: '3'},
    ])
  })
  it('Generates a redacted set of rating options', () => {
    expect(ratingsNonExtreme()).toEqual([
      {text: 'Clean/Safe for work', value: '0'},
      {text: 'Risque/mature, not adult content but not safe for work', value: '1'},
      {text: 'Adult content, not safe for work', value: '2'},
    ])
  })
  it('Generates a standard schema for submission upload', () => {
    wrapper = shallowMount(Empty, {localVue, store})
    const handler = wrapper.vm.$getProfile('person', {})
    expect(newUploadSchema(handler.user)).toEqual({
      endpoint: `/api/profiles/v1/account/person/submissions/`,
      fields: {
        title: {value: ''},
        caption: {value: ''},
        private: {value: false},
        comments_disabled: {value: false},
        rating: {value: 0, step: 2},
        file: {value: '', step: 3},
        preview: {value: '', step: 3},
        tags: {value: [], step: 2},
        characters: {value: [], step: 2},
        artists: {value: [], step: 2},
      },
    })
  })
})
describe('HTTP Helpers', () => {
  it('Constructs the appropriate headers for a POST request', () => {
    setCookie('csrftoken', 'Stuff')
    setCookie('referredBy', 'Jimmy')
    expect(getHeaders('post', '/test/')).toEqual(
      {'Content-Type': 'application/json; charset=utf-8', 'X-CSRFToken': 'Stuff', 'X-Referred-By': 'Jimmy'}
    )
  })
  it('Constructs the appropriate headers for an outside POST request', () => {
    setCookie('csrftoken', 'Stuff')
    expect(getHeaders('post', 'https://example.com/')).toEqual(
      {'Content-Type': 'application/json; charset=utf-8'}
    )
  })
  it('Constructs the appropriate headers for a GET request', () => {
    setCookie('csrftoken', 'Stuff')
    expect(getHeaders('get', '/test/')).toEqual(
      {'Content-Type': 'application/json; charset=utf-8'}
    )
  })
  it.each`
    url                      | result
    ${'https://example.com/'}| ${true}
    ${'//test.com/thing'}    | ${true}
    ${window.location}       | ${false}
    ${'/'}                   | ${false}
  `('should determine the cross-domain status of $url to be $result.',
  ({url, result}) => {
    expect(crossDomain(url)).toBe(result)
  })
  it.each`
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
  it('Sets a cookie', () => {
    setCookie('test', 'value')
    expect(getCookie('test')).toBe('value')
  })
  it('Sets a cookie with an expiration date', () => {
    setCookie('test', 'value', 1)
    // We can't actually check if the date was set correctly, just that coverage said the appropriate code ran.
    expect(getCookie('test')).toBe('value')
  })
})
describe('Formatters', () => {
  beforeEach(() => {
    moment.tz.setDefault('America/Chicago')
  })
  afterEach(() => {
    moment.tz.setDefault()
  })
  it('Formats a datetime string', () => {
    expect(formatDateTime('2019-05-03T15:41:36.902Z')).toBe('May 3rd 2019, 10:41:36 am')
  })
  it('Formats a date string', () => {
    expect(formatDate('2019-05-03')).toBe('May 3rd 2019')
  })
  it('Formats a datetime string as a date', () => {
    expect(formatDate('2019-05-03T15:41:36.902Z')).toBe('May 3rd 2019')
  })
  it('Does not truncate text that is under the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 50)).toBe(
      'This is a test string. It is 49 characters long.'
    )
  })
  it('Truncates text that is over the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 4)).toBe('This...')
  })
  it('Truncates before the space when over the limit', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 5)).toBe('This...')
  })
  it('Does not truncate text mid-word if it can be avoided', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 12)).toBe(
      'This is a...'
    )
  })
  it('Truncates mid-word if it has no other choice', () => {
    expect(truncateText('This is a test string. It is 49 characters long.', 2)).toBe(
      'Th...'
    )
  })
  it.each`
    size             | result
    ${1000}          | ${'1000 B'}
    ${10000}         | ${'9.77 KB'}
    ${10000000}      | ${'9.54 MB'}
    ${10000000000}   | ${'9.31 GB'}
    ${10000000000000}| ${'9.09 TB'}
  `('Makes the byte size $size human readable as $result', ({size, result}) => {
  expect(formatSize(size)).toBe(result)
})
  it('Renders markdown with links', () => {
    expect(md.render(`# Hello there.

*This is a test of the markdown renderer.* **There is no need to be alarmed.**
<a href='https://example.com/'>I'm going to try a manual link.</a>

[Here's a markdown link](http://example.com/)

[Here's another markdown link](/)

Here's a raw link: https://example.com/

Here's an email: support@artconomy.com`)).toBe(`<h1>Hello there.</h1>
<p><em>This is a test of the markdown renderer.</em> <strong>There is no need to be alarmed.</strong><br>
&lt;a href='<a href="https://example.com/'%3EI'm" target="_blank" rel="nofollow">https://example.com/'&gt;I'm</a> going to try a manual link.&lt;/a&gt;</p>
<p><a href="http://example.com/" target="_blank" rel="nofollow">Here's a markdown link</a></p>
<p><a href="/" target="_blank" onclick="artconomy.$router.history.push('/');return false">Here's another markdown link</a></p>
<p>Here's a raw link: <a href="https://example.com/" target="_blank" rel="nofollow">https://example.com/</a></p>
<p>Here's an email: <a href="mailto:support@artconomy.com" target="_blank">support@artconomy.com</a></p>
`)
  })
  it('Does not render links if prerender is set to true', () => {
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
  it('Renders markdown with Avatars', () => {
    expect(md.render(
      `Hello, @Foxie. Is this @Vulpine creature as cute as I'd hope? Maybe @Fox's tricks will tell us.`)).toBe(
      `<p>Hello, <span style="display:inline-block;vertical-align: bottom;"><ac-avatar username="Foxie">` +
      `</ac-avatar></span>. Is this <span style="display:inline-block;vertical-align: bottom;">` +
      `<ac-avatar username="Vulpine"></ac-avatar></span> creature as cute as I'd hope? Maybe ` +
      `<span style="display:inline-block;vertical-align: bottom;">` +
      `<ac-avatar username="Fox"></ac-avatar></span>'s tricks will tell us.</p>
`)
  })
  it.each`
    input                           | result
    ${'lists'}                      | ${'lists'}
    ${'lists/thing'}                | ${'lists_thing'}
    ${'stuff.wut'}                  | ${'stuff_wut'}
    ${'this.thing/is/quite.nested'} | ${'this_thing_is_quite_nested'}
  `('Should flatten $input into $result', ({input, result}) => {
  expect(flatten(input)).toBe(result)
})
  it.each`
  userList                       | additional    | result
  ${['user1', 'user2', 'user3']} | ${0}          | ${'user1, user2, and user3'}
  ${['user1', 'user2', 'user3']} | ${3}          | ${'user1, user2, user3 and 3 others'}
  ${['user1', 'user2', 'user3']} | ${1}          | ${'user1, user2, user3 and 1 other'}
  ${['user1', 'user2']}          | ${0}          | ${'user1 and user2'}
  ${['user1']}                   | ${0}          | ${'user1'}
  `('Should format a posse', ({userList, additional, result}) => {
  expect(posse(userList, additional)).toEqual(result)
})
  it.each`
  userName  | result
  ${'_'}    | ${''}
  ${'__4'}  | ${'Guest #4'}
  ${'Fox'}  | ${'Fox'}
  ${null}   | ${''}
  `('Should format a display name based on a username', ({userName, result}) => {
  expect(deriveDisplayName(userName)).toBe(result)
})
  it.each`
  userName       | result
  ${'Guest #5'}  | ${true}
  ${'__5'}       | ${true}
  ${'Fox'}       | ${false}
  `('Can determine whether a username belongs to a guest account', ({userName, result}) => {
  expect(guestName(userName)).toBe(result)
})
})

describe('Path helpers', () => {
  it.each`
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

describe('Tab manager', () => {
  const localVue = createLocalVue()
  localVue.use(VueRouter)
  let router: VueRouter
  beforeEach(() => {
    router = new VueRouter({
      mode: 'history',
      routes: [{
        path: '/place/:tabName/:subTabName?',
        name: 'Settings',
        component: ParamTabbed,
        props: true,
      }],
    })
  })
  it('Syncs tab parameter with router', () => {
    router.push('/place/somewhere/')
    const wrapper = mount(Routed, {localVue, router})
    const current = (wrapper.vm as any).$refs.current
    expect(current.tab).toBe('tab-somewhere')
    current.tab = 'nowhere'
    expect(current.$route.params.tabName).toBe('nowhere')
  })
  it('Handles default option', () => {
    router.push('/place/somewhere/')
    const wrapper = mount(Routed, {localVue, router})
    const current = (wrapper.vm as any).$refs.current
    expect(current.subTab).toBe('tab-two')
  })
  it('Replaces invalid option with default', () => {
    router.push('/place/somewhere/wat')
    const wrapper = mount(Routed, {localVue, router})
    const current = (wrapper.vm as any).$refs.current
    expect(current.subTab).toBe('tab-two')
  })
  it('Blanks on invalid option when no default is set', () => {
    router.push('/place/somewhere/wat')
    const wrapper = mount(Routed, {localVue, router})
    const current = (wrapper.vm as any).$refs.current
    expect(current.subTab2).toBe('')
  })
  it('Resets other tabs when changed', () => {
    router.push('/place/somewhere/one')
    const wrapper = mount(Routed, {localVue, router})
    const current = (wrapper.vm as any).$refs.current
    expect(current.subTab).toBe('tab-one')
    current.altTab = 'dude'
    expect(current.$route.params).toEqual({tabName: 'dude'})
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
  it('Traverses a tree to find a particular result and an end branch', () => {
    expect(dotTraverse(item, 'thing.stuff.wat')).toBe('Yay')
  })
  it('Traverses a tree to find a result mid-branch', () => {
    expect(dotTraverse(item, 'thing.stuff')).toEqual({wat: 'Yay'})
  })
  it('Raises an exception if the path does not exist', () => {
    expect(() => dotTraverse(item, 'thing.stuff.org.wat')).toThrow(
      Error(`Property thing.stuff.org is not defined.`)
    )
  })
  it('Returns undefined if silenced and the path does not exist', () => {
    expect(dotTraverse(item, 'thing.stuff.org.wat', true)).toBe(undefined)
  })
})

describe('thumbFromSpec', () => {
  it('Returns the full image by default if the thumbnail is not present', () => {
    const file = {full: '/thing/wat.jpg', type: 'data:image'}
    expect(thumbFromSpec('thumbnail', file)).toBe('/thing/wat.jpg')
  })
  it('Returns the correct thumbnail', () => {
    const file = {full: '/thing/wat.jpg', thumbnail: '/stuff/things.jpg', type: 'data:image'}
    expect(thumbFromSpec('thumbnail', file)).toBe('/stuff/things.jpg')
  })
})

describe('makeQueryParams', () => {
  it('Wat', () => {
    const testData = {stuff: false, things: true, wat: 2}
    expect(makeQueryParams(testData)).toEqual({stuff: 'false', things: 'true', wat: '2'})
  })
})
