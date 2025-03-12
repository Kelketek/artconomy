import { computed, ref, watch } from "vue"
import { HttpStatusCode } from "axios"

export const createStatusHeader = () => {
  const tag = document.createElement("meta")
  tag.setAttribute("name", "prerender-status-code")
  document.head.appendChild(tag)
  return tag
}

export const setStatus = (statusCode: HttpStatusCode) => {
  // <meta name="prerender-status-code" content="404">
  const statusHeader =
    document.querySelector('meta[name="prerender-status-code"]') ||
    createStatusHeader()
  statusHeader.setAttribute("content", statusCode + "")
}

export const getHeaders = () => {
  return Object.fromEntries(
    Array.from(document.querySelectorAll('meta[name="prerender-header"]')).map(
      (element: Element) => {
        // <meta name="prerender-header" content="Location: https://www.google.com">
        return [...(element.getAttribute("content") || ": ").split(": ", 2)]
      },
    ),
  )
}

export const replaceHeaderValues = (toSet: [string, string][]) => {
  document
    .querySelectorAll('meta[name="prerender-header"]')
    .forEach((element) => element.remove())
  toSet.forEach(([key, value]) => {
    const tag = document.createElement("meta")
    tag.setAttribute("name", "prerender-header")
    tag.setAttribute("content", `${key}: ${value}`)
    document.head.appendChild(tag)
  })
}

export const setHeaders = (headers: { [key: string]: string | string[] }) => {
  const toSet: [string, string][] = []
  Object.entries(headers).reduce((all, currentEntry) => {
    const [key, value] = currentEntry
    if (Array.isArray(value)) {
      for (const item in value) {
        all.push([key, item])
      }
    } else {
      all.push([key, value])
    }
    return all
  }, toSet)
  replaceHeaderValues(toSet)
}

export const replaceHeader = (key: string, value: string | string[]) => {
  const headers = getHeaders()
  headers[key] = value
  setHeaders(headers)
}

export const redirect = (url: string, permanent?: true) => {
  const status = permanent
    ? HttpStatusCode.PermanentRedirect
    : HttpStatusCode.TemporaryRedirect
  setStatus(status)
  replaceHeader("Location", url)
}

export const usePrerendering = () => {
  const prerendering = ref(!!window.PRERENDERING)
  watch(
    () => window.PRERENDERING,
    () => (prerendering.value = !!window.PRERENDERING),
  )
  return {
    prerendering: computed(() => !!window.PRERENDERING),
  }
}
