// This snow generator is a cleaned up version of the one found here:
// https://github.com/radkinz/snow.js/blob/master/snow.js

export interface SnowOptions {
  id: string
  minSize?: number
  maxSize?: number
  zIndex?: number
  count?: number
}

export interface SnowController {
  element: HTMLElement
  canvas: HTMLCanvasElement
  stop: () => void
  start: () => void
  clear: () => void
  toggle: () => void
  isRunning: () => boolean
}

export interface FlakeState {
  x: number
  y: number
  vY: number
  color: string
}

export interface SnowFlake {
  show: () => void
  update: () => void
  state: FlakeState
}

const random = (min: number, max: number) => {
  return Math.random() * (max - min) + min
}

//snowflakes to use in snow
const makeFlake = (canvas: HTMLCanvasElement, min: number, max: number) => {
  const state = {
    radius: random(min, max),
    x: random(0, canvas.width),
    y: random(-20, -800),
    vY: random(1, 2),
    color: "#FFF",
  }

  const show = function () {
    const ctx = canvas.getContext("2d")!
    ctx.beginPath()
    ctx.arc(state.x, state.y, state.radius, 0, 2 * Math.PI)
    ctx.closePath()
    ctx.fillStyle = state.color
    ctx.fill()
  }

  const update = function () {
    state.y += state.vY
  }
  return { show, update, state }
}

export const buildSnow = (options: SnowOptions): SnowController => {
  const element = document.getElementById(options.id)
  if (!element) {
    throw Error(`Could not find element with id ${options.id}`)
  }
  element.style.position = "fixed"
  element.style.top = "0"
  element.style.left = "0"
  element.style.right = "0"
  element.style.bottom = "0"
  element.style.zIndex = String(options.zIndex ?? 1000)
  element.style.pointerEvents = "none"

  const canvas = document.createElement("canvas") //add random number to change canvas id
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  element.appendChild(canvas)

  //change size
  const min = options.minSize ?? 2
  const max = options.maxSize ?? 7
  const count = options.count ?? 250

  //snowflake list
  const snowflakes: SnowFlake[] = []

  for (let i = 0; i < count; i++) {
    const flake = makeFlake(canvas, min, max)
    snowflakes.push(flake)
    flake.show()
  }

  let go = false
  const snowfall = function () {
    requestAnimationFrame(() => snowfall())

    if (go) {
      //clear canvas
      const context = canvas.getContext("2d")!
      context.clearRect(0, 0, canvas.width, canvas.height)

      //update snowflakes
      for (const flake of snowflakes) {
        flake.update()
        flake.show()

        if (flake.state.y > canvas.height) {
          flake.state.y = random(-20, -200)
        }
      }
    }
  }

  snowfall()

  const start = function () {
    go = true
  }

  const stop = function () {
    go = false
  }

  const toggle = function () {
    go = !go
    return go
  }
  const isRunning = function () {
    return go
  }
  const clear = function () {
    stop()
    snowflakes.length = 0
    canvas.remove()
  }
  return {
    element,
    canvas,
    start,
    stop,
    clear,
    toggle,
    isRunning,
  }
}
