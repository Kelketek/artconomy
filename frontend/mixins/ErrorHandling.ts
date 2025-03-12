import { AxiosError } from "axios"
import { useStore } from "vuex"

export const statusOk = (...statuses: number[]) => {
  return (error: AxiosError) => {
    if (error.response && statuses.indexOf(error.response.status) !== -1) {
      return
    }
    throw error
  }
}

export const useErrorHandling = () => {
  const store = useStore()
  const setError = (error: Error) => {
    store.commit("errors/setError", error)
  }
  return { setError, statusOk }
}
