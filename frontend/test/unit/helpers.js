import fieldCharacterSearch from '../../src/components/fields/fieldCharacterSearch'
import fieldUserSearch from '../../src/components/fields/fieldUserSearch'
import fieldTagSearch from '../../src/components/fields/fieldTagSearch'
import fieldRecaptcha from '../../src/components/fields/fieldRecaptcha'
import fieldVText from '../../src/components/fields/fieldVText'
import fieldVCheckbox from '../../src/components/fields/fieldVCheckbox'
import fieldVSelect from '../../src/components/fields/fieldVSelect'
import fieldVFileUpload from '../../src/components/fields/fieldVFileUpload'
import fieldVColor from '../../src/components/fields/fieldVColor'

export function checkJson (request, expected) {
  for (let key in expected) {
    if (key === 'data') {
      continue
    }
    expect(request[key]).to.deep.equal(expected[key])
  }
  let result = JSON.parse(request['requestBody'])
  expect(expected['data']).to.deep.equal(result)
}

export function waitFor (func, message, timeout) {
  return new Promise(function (resolve, reject) {
    if (!timeout) {
      timeout = 5
    }
    let timer = 0
    timeout *= 1000;
    (function waitForCondition () {
      console.log(func())
      if (func()) return resolve()
      timer += 1
      if (timer >= timeout) return reject(Error(message))
      setTimeout(waitForCondition, 200)
    })()
  })
}

export function isVisible (wrapper) {
  // Naive visibility checker
  let classList = wrapper.element.className.split(' ')
  let tests = [
    getComputedStyle(wrapper.element, null).getPropertyValue('display') === 'none',
    (classList.includes('fade') && !(classList.includes('active') || classList.includes('show')))
  ]
  return (!tests.includes(true))
}

export function installFields (localVue) {
  localVue.component('fieldCharacterSearch', fieldCharacterSearch)
  localVue.component('fieldUserSearch', fieldUserSearch)
  localVue.component('fieldTagSearch', fieldTagSearch)
  localVue.component('fieldRecaptcha', fieldRecaptcha)
  localVue.component('fieldVText', fieldVText)
  localVue.component('fieldVCheckbox', fieldVCheckbox)
  localVue.component('fieldVSelect', fieldVSelect)
  localVue.component('fieldVFileUpload', fieldVFileUpload)
  localVue.component('fieldVColor', fieldVColor)
}
