import {Component} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'
import {computed} from 'vue'

@Component
export default class Upload extends ArtVue {
  public get showUpload() {
    return this.$store.state.uploadVisible
  }

  public set showUpload(val: boolean) {
    this.$store.commit('setUploadVisible', val)
  }
}

export const useUpload = () => {
  const store = useStore<ArtState>()
  const showUpload = computed({
    get() {
      return store.state.uploadVisible
    },
    set(val: boolean) {
      store.commit('setUploadVisible', val)
    }
  })
  return {showUpload}
}
