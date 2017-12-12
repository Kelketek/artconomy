import Simple from '../fixtures/ac-patch-field/Simple'
import { mount, createLocalVue } from 'vue-test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'

let server, localVue

describe('ac-patch-field.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.prototype.md = MarkDownIt()
  })
  afterEach(function () {
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
  it('Becomes editable for multi line if clicked on when edit mode is enabled.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        multiline: true,
        value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
        'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
        'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit',
        editing: true
      }
    })
    expect(wrapper.text()).to.equal(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n' +
      'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget\n' +
      'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
    )
    expect(wrapper.find('textarea').exists()).to.equal(false)
    expect(wrapper.find('.patchfield-normal').exists()).to.equal(false)
    let field = wrapper.find('.patchfield-preview')
    expect(field.exists()).to.equal(true)
    field.trigger('click')
    await localVue.nextTick()
    expect(wrapper.find('textarea').exists()).to.equal(true)
    expect(wrapper.find('textarea').element.value).to.equal(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
      'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
      'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
    )
  })
  it('Does not submit a change and becomes uneditable if blurred after clicked without an edit (single line).', async() => {
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
    wrapper.find('input').trigger('blur')
    await localVue.nextTick()
    expect(server.requests.length).to.equal(0)
    expect(wrapper.find('input').exists()).to.equal(false)
    expect(wrapper.text()).to.equal('TestValue')
  })
  it('Does not submit a change and becomes uneditable if blurred after clicked without an edit (multi line).', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        multiline: true,
        value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
        'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
        'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit',
        editing: true
      }
    })
    let field = wrapper.find('.patchfield-preview')
    field.trigger('click')
    await localVue.nextTick()
    wrapper.find('textarea').trigger('blur')
    await localVue.nextTick()
    expect(server.requests.length).to.equal(0)
    expect(wrapper.find('textarea').exists()).to.equal(false)
    expect(wrapper.text()).to.equal(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n' +
      'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget\n' +
      'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
    )
  })
  it('Submits a change and becomes uneditable if blurred after clicked with an edit (single line).', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue',
        editing: true,
        name: 'test'
      }
    })
    let field = wrapper.find('.patchfield-preview')
    field.trigger('click')
    await localVue.nextTick()
    let input = wrapper.find('input')
    input.element.value = 'New Value'
    wrapper.find('input').trigger('blur')
    await localVue.nextTick()
    expect(server.requests.length).to.equal(1)
    expect(input.element.getAttribute('disabled')).to.equal('disabled')
    server.requests[0].respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify({'test': 'New Value'})
    )
    await localVue.nextTick()
    expect(wrapper.find('input').exists()).to.equal(false)
    expect(wrapper.text()).to.equal('New Value')
  })
  it('Submits a change and becomes uneditable if blurred after clicked with an edit (multi line).', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        multiline: true,
        value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. \n\n' +
        'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget \n\n' +
        'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit',
        editing: true
      }
    })
    let field = wrapper.find('.patchfield-preview')
    field.trigger('click')
    await localVue.nextTick()
    let input = wrapper.find('textarea')
    input.element.value = 'New Value'
    wrapper.find('textarea').trigger('blur')
    await localVue.nextTick()
    expect(server.requests.length).to.equal(1)
    expect(input.element.getAttribute('disabled')).to.equal('disabled')
    server.requests[0].respond(
      200,
      { 'Content-Type': 'application/json' },
      JSON.stringify({'test': 'New Value'})
    )
    await localVue.nextTick()
    expect(wrapper.find('textarea').exists()).to.equal(false)
    expect(wrapper.text()).to.equal('New Value')
  })
})
