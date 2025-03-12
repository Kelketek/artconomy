import { useStore } from "vuex"
import { ArtState } from "@/store/artState.ts"
import { computed } from "vue"

export const useUpload = () => {
  const store = useStore<ArtState>()
  const showUpload = computed({
    get() {
      return store.state.uploadVisible
    },
    set(val: boolean) {
      store.commit("setUploadVisible", val)
    },
  })
  return { showUpload }
}
