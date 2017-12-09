import Simple from '../fixtures/ac-patch-field/Simple'
import { mount, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import $ from 'jquery'
import sinon from 'sinon'

let server, localVue

describe('Character.vue', () => {
  before(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
  })
  after(function () {
    server.restore()
  })
  it('Displays normal information for single line.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue'
      }
    })
    expect(wrapper.text()).to.equal('TestValue')
  })
  it('Displays normal information for multiple lines.', async() => {
    let wrapper = mount(
      Simple, {
        localVue,
        propsData: {
          multiline: true,
          value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
          'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
          'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
        }
      })
    expect(wrapper.text()).to.equal(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n' +
      'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget\n' +
      'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
    )
  })
  it('Does not become editable for a single line if clicked on when edit mode is not enabled.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue'
      }
    })
    expect(wrapper.find('input').exists()).to.equal(false)
    let field = wrapper.find('.patchfield-normal')
    expect(field.exists()).to.equal(true)
    field.trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('input').exists()).to.equal(false)
  })
  it('Does not become editable for multiple lines if clicked on when edit mode is not enabled.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        multiline: true,
        value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
        'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
        'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
      }
    })
    expect(wrapper.find('input').exists()).to.equal(false)
    let field = wrapper.find('.patchfield-normal')
    expect(field.exists()).to.equal(true)
    field.trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('input').exists()).to.equal(false)
  })
  it('Becomes editable for a single line if clicked on when edit mode is enabled.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue',
        editing: true
      }
    })
    expect(wrapper.text()).to.equal('TestValue')
    expect(wrapper.find('input').exists()).to.equal(false)
    expect(wrapper.find('.patchfield-normal').exists()).to.equal(false)
    let field = wrapper.find('.patchfield-preview')
    expect(field.exists()).to.equal(true)
    field.trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('input').exists()).to.equal(true)
    expect(wrapper.find('input').element.value).to.equal('TestValue')
  })
  it('Does not submit a change and becomes uneditable if blurred after clicked without an edit..', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue',
        editing: true
      }
    })
    let field = wrapper.find('.patchfield-preview')
    field.trigger('click')
    await localVue.nextTick()
    // jQuery's click is more reliable for sending blurs.
    $(field.element).blur()
    await localVue.nextTick()
    expect(server.requests.length).to.equal(0)
    expect(wrapper.find('input').exists()).to.equal(false)
    expect(wrapper.text()).to.equal('TestValue')
  })
})
