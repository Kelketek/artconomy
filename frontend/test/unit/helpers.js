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
    let timer = 0;
    (function waitForCondition () {
      if (func()) return resolve()
      timer += 1
      if (timer >= timeout) return reject(Error(message))
      setTimeout(waitForCondition, 1)
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
