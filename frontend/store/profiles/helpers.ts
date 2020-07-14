export function artistProfileEndpointFor(username: string) {
  return `/api/profiles/v1/account/${username}/artist-profile/`
}

export function artistProfilePathFor(username: string) {
  return [...pathFor(username), 'artistProfile']
}

export function pathFor(username: string) {
  return ['userModules', username]
}

export function userPathFor(username: string) {
  return [...pathFor(username), 'user']
}

export function endpointFor(username: string) {
  if (username === '_') {
    return '/api/profiles/v1/data/requester/'
  }
  return `/api/profiles/v1/account/${username}/`
}
