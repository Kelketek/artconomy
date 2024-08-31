export function artistProfileEndpointFor(username: string) {
  return `/api/profiles/account/${username}/artist-profile/`
}

export function artistProfilePathFor(username: string) {
  return [...pathFor(username), 'artistProfile']
}

export function staffPowersPathFor(username: string) {
  return [...pathFor(username), 'staffPowers']
}

export function staffPowersEndpointFor(username: string) {
  return `/api/profiles/account/${username}/staff-powers/`
}

export function pathFor(username: string) {
  return ['userModules', username]
}

export function userPathFor(username: string) {
  return [...pathFor(username), 'user']
}

export function endpointFor(username: string) {
  if (username === '_') {
    return '/api/profiles/data/requester/'
  }
  return `/api/profiles/account/${username}/`
}
