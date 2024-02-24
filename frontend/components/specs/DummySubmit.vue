<template>
  <v-app>
    <v-main>
      <ac-new-submission ref="submissionForm" title="Sharable thing!" :username="username" v-model="showUpload"
                         :allow-multiple="allowMultiple"/>
    </v-main>
  </v-app>
</template>
<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import Upload from '@/mixins/upload.ts'
import {defineAsyncComponent} from 'vue'
const AcNewSubmission = defineAsyncComponent(() => import('@/components/AcNewSubmission.vue'))

@Component({
  components: {AcNewSubmission},
})
class DummySubmit extends mixins(Subjective, Upload) {
  @Prop({default: false})
  public allowMultiple!: boolean

  public created() {
    this.showUpload = true
  }
}

export default toNative(DummySubmit)
</script>
