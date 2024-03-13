import Token from 'markdown-it/lib/token'
import {Options} from 'markdown-it/lib'
import Renderer from 'markdown-it/lib/renderer'
import StateInline from 'markdown-it/lib/rules_inline/state_inline'
import {format, parseISO as upstreamParseISO} from 'date-fns'
import {markRaw} from 'vue'
import MarkDownIt from 'markdown-it'

export const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) {
    return text
  }
  const newText = text.slice(0, maxLength)
  let iterator = 0
  // Find the first space break before that point.
  while (iterator < newText.length) {
    const testText = newText.slice(0, newText.length - iterator)
    if (([' ', '\n', '\r', '\t'].indexOf(testText[testText.length - 1]) === -1)) {
      iterator += 1
      continue
    }
    return testText.trimEnd() + '...'
  }
  // Super long word for some reason.
  return newText + '...'
}
export const md = markRaw(new MarkDownIt({
  linkify: true,
  breaks: true,
}))
type TokenRenderer = (
  tokens: Token[], idx: number, options: Options, env: any, self: Renderer,
) => string
export const defaultRender: TokenRenderer = (
  tokens: Token[], idx: number, options: Options, env: any, self: Renderer,
): string => {
  return self.renderToken(tokens, idx, options)
}

export function isForeign(url: string) {
  if (url.toLowerCase().startsWith('mailto:')) {
    return false
  }
  // noinspection RedundantIfStatementJS
  if (url.startsWith('/') ||
    url.match(/^http(s)?:[/][/](www[.])?artconomy[.]com([/]|$)/) ||
    url.match(/^http(s)?:[/][/]artconomy[.]vulpinity[.]com([/]|$)/)) {
    return false
  }
  return true
}

export function mention(state: StateInline, silent: boolean) {
  let token: Token
  let pos = state.pos
  const ch = state.src.charCodeAt(pos)

  // Bug out if this @ is in the middle of a word instead of the beginning.
  const prCh = state.src[pos - 1]
  if (prCh !== undefined) {
    if (!/^\s+$/.test(prCh)) {
      return false
    }
  }
  if (ch !== 0x40/* @ */) {
    return false
  }
  const start = pos
  pos++
  const max = state.posMax

  while (pos < max && /[-a-zA-Z_0-9]/.test(state.src[pos])) {
    pos++
  }
  if (pos - start === 1) {
    // Hanging @.
    return false
  }

  const marker = state.src.slice(start, pos)
  // Never found an instance where this is true, but the MarkdownIt rules require handling it.
  /* istanbul ignore else */
  if (!silent) {
    token = state.push('mention', 'ac-avatar', 0)
    token.content = marker
    state.pos = pos
    return true
  }
  return false
}

export function parseISO(dateString: string | Date) {
  // Mimics moment's behavior of taking either a string or a date and returning a date.
  if (dateString instanceof Date) {
    return dateString
  }
  return upstreamParseISO(dateString)
}

export function formatDateTime(dateString: string) {
  return format(parseISO(dateString), 'MMMM do yyyy, h:mm:ss aaa')
}

export function formatDate(dateString: string) {
  return format(parseISO(dateString), 'MMMM do yyyy')
}

export function formatDateTerse(dateString: string | Date) {
  const date = parseISO(dateString)
  if (date.getFullYear() !== new Date().getFullYear()) {
    return format(date, 'MMM do yy')
  }
  return format(date, 'MMM do')
}

export function textualize(markdown: string) {
  const container = document.createElement('div')
  container.innerHTML = md.render(markdown)
  return (container.textContent && container.textContent.trim()) || ''
}

export function formatSize(size: number): string {
  if (size > 1024 * 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024 / 1024).toFixed(2) + ' TB'
  } else if (size > 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB'
  } else if (size > 1024 * 1024) {
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  } else if (size > 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  }
  return size.toString() + ' B'
}

export function deriveDisplayName(username: string) {
  if (!username) {
    return ''
  }
  if (username === '_') {
    return ''
  }
  if (username.startsWith('__deleted')) {
    return '[deleted]'
  }
  if (username.startsWith('__')) {
    // @ts-ignore
    return `Guest #${username.match(/__([0-9]+)/)[1]}`
  }
  return username
}

export function guestName(username: string) {
  if (username.indexOf(' #') !== -1) {
    return true
  }
  return (username.startsWith('__'))
}
