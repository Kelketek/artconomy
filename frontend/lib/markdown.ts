import { markRaw } from "vue"
import markdownit from "markdown-it"
import Token from "markdown-it/lib/token"
import { Options } from "markdown-it/lib"
import Renderer from "markdown-it/lib/renderer"
import StateInline from "markdown-it/lib/rules_inline/state_inline"

export const md = markRaw(
  markdownit({
    linkify: true,
    breaks: true,
  }),
)
type TokenRenderer = (
  tokens: Token[],
  idx: number,
  options: Options,
  env: any,
  self: Renderer,
) => string
export const defaultRender: TokenRenderer = (
  tokens: Token[],
  idx: number,
  options: Options,
  env: any,
  self: Renderer,
): string => {
  return self.renderToken(tokens, idx, options)
}

export function isForeign(url: string) {
  if (url.toLowerCase().startsWith("mailto:")) {
    return false
  }
  // noinspection RedundantIfStatementJS
  if (
    url.startsWith("/") ||
    url.match(/^http(s)?:[/][/](www[.])?artconomy[.]com([/]|$)/) ||
    url.match(/^http(s)?:[/][/]artconomy[.]vulpinity[.]com([/]|$)/)
  ) {
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
  if (ch !== 0x40 /* @ */) {
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
    token = state.push("mention", "ac-avatar", 0)
    token.content = marker
    state.pos = pos
    return true
  }
  return false
}

export function textualize(markdown: string) {
  const container = document.createElement("div")
  container.innerHTML = md.render(markdown)
  return (container.textContent && container.textContent.trim()) || ""
}

md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  if (window.PRERENDERING) {
    return tokens[idx].content
  }
  tokens[idx].attrPush(["target", "_blank"]) // add new attribute
  const hrefIndex = tokens[idx].attrIndex("href")
  // Should always have href for a link.
  let href = tokens[idx].attrs![hrefIndex][1]
  if (isForeign(href)) {
    tokens[idx].attrPush(["rel", "nofollow noopener"])
    return defaultRender(tokens, idx, options, env, self)
  }
  // Local dev URL format.
  href = href.replace(/^http(s)?:[/][/]artconomy[.]vulpinity[.]com([/]|$)/, "/")
  // Public server format.
  href = href.replace(/^http(s)?:[/][/](www[.])?artconomy[.]com([/]|$)/, "/")
  href = encodeURI(href)
  if (!href.startsWith("mailto:")) {
    tokens[idx].attrPush([
      "onclick",
      `artconomy.$router.push('${href}').catch(() => {});return false`,
    ])
  }
  return defaultRender(tokens, idx, options, env, self)
}

md.renderer.rules.link_close = (tokens, idx, options, env, self) => {
  if (window.PRERENDERING) {
    return ""
  }
  return defaultRender(tokens, idx, options, env, self)
}

md.renderer.rules.mention = (tokens, idx) => {
  const token = tokens[idx]
  const username = token.content.slice(1, token.content.length)
  // Must have no returns, or will affect spacing.
  const url = `/profile/${encodeURIComponent(username)}/about`
  return `<a href="${url}" onclick="artconomy.$router.push('${url}');return false">@${username}</a>`
}

md.inline.ruler.push("mention", mention, { alt: ["mention"] })
