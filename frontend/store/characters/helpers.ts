export function characterEndpoint(username: string, characterName: string) {
  return `/api/profiles/account/${username}/characters/${characterName}/`
}
