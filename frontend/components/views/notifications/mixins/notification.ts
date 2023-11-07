import {toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer'
import {defineComponent, PropType} from 'vue'
import AcNotification from '@/types/AcNotification'


export default defineComponent({
  // Not sure why, but toNative is not being respected here for typing, even though it works.
  mixins: [toNative(Viewer) as any],
  props: {notification: {type: Object as PropType<AcNotification<any, any>>, required: true}},
  computed: {
    event() {
      return this.notification.event
    },
  },
})
