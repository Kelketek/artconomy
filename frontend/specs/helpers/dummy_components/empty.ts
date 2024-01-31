import {h} from 'vue'
import {Component, toNative} from 'vue-facing-decorator'
import {ArtVue} from '@/lib/lib'

@Component
class Empty extends ArtVue {
  render() {
    return h('div')
  }
}
export default toNative(Empty)