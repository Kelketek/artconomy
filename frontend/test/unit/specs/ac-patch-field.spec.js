import Simple from '../fixtures/ac-patch-field/Simple'
import { mount, createLocalVue } from '@vue/test-utils'
import MarkDownIt from 'markdown-it'
import sinon from 'sinon'
import Vuetify from 'vuetify'

let server, localVue

describe('ac-patch-field.vue', () => {
  beforeEach(function () {
    server = sinon.fakeServer.create()
    localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.prototype.md = MarkDownIt()
  })
  afterEach(function () {
    server.restore()
  })
  it('Displays normal information for single line.', async() => {
    let wrapper = mount(Simple, {
      localVue,
      propsData: {
        value: 'TestValue',
        name: 'test'
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
          'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit',
          name: 'test'
        }
      })
    expect(wrapper.text()).to.equal(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n' +
      'Duis ac libero facilisis, hendrerit risus in, pulvinar ex. Ut placerat mi odio, eget\n' +
      'iaculis lectus volutpat ullamcorper. Etiam ut eros at massa porttitor faucibus sit'
    )
  })
})
