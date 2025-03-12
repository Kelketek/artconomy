import { Alert, AlertCategory, ArtState } from "@/store/artState.ts"
import { useStore } from "vuex"

export const useAlerts = () => {
  const store = useStore<ArtState>()
  const sendAlert = (alert: Partial<Alert> & { message: Alert["message"] }) => {
    store.commit("pushAlert", {
      timeout: 5000,
      category: AlertCategory.INFO,
      ...alert,
    })
  }
  return { sendAlert }
}
