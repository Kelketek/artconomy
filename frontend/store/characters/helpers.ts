export function characterEndpoint(username: string, characterName: string) {
  return `/api/profiles/v1/account/${username}/characters/${characterName}/`
}
