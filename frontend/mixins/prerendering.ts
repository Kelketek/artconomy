export const usePrerendering = () => {
  return {
    prerendering: !!window.PRERENDERING
  }
}
