import Vue from 'vue'
import Component from 'vue-class-component'
import {Mutation, State} from 'vuex-class'

@Component
export default class Upload extends Vue {
  @State('uploadVisible') public uploadVisible!: boolean
  @Mutation('setUploadVisible') public setUploadVisible: any

  public get showUpload() {
    return this.uploadVisible
  }
  public set showUpload(val: boolean) {
    this.setUploadVisible(val)
  }
}
