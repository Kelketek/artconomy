import {Component} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib.ts'

@Component
export default class Upload extends ArtVue {
  public get showUpload() {
    return this.$store.state.uploadVisible
  }

  public set showUpload(val: boolean) {
    this.$store.commit('setUploadVisible', val)
  }
}
