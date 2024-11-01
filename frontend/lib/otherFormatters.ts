import {format, parseISO as upstreamParseISO} from 'date-fns'

import {RelatedUser, TerseUser, User} from '@/store/profiles/types/main'

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

export function posse(userList: string[], additional: number) {
  userList = userList.map((username) => deriveDisplayName(username))
  if (userList.length === 2 && !additional) {
    return `${userList[0]} and ${userList[1]}`
  }
  if (userList.length === 3 && !additional) {
    return `${userList[0]}, ${userList[1]}, and ${userList[2]}`
  }
  let group = userList.join(', ')
  if (additional) {
    group += ' and ' + additional
    if (additional === 1) {
      group += ' other'
    } else {
      group += ' others'
    }
  }
  return group
}

export function profileLink(user: User | TerseUser | RelatedUser | null) {
  if (!user) {
    return null
  }
  if (guestName(user.username)) {
    return null
  }
  return {
    name: 'AboutUser',
    params: {username: user.username},
  }
}
