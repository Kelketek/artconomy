<template>
  <v-app>
    <v-main>
      <ac-new-submission ref="submissionForm" title="Sharable thing!" :username="username" v-model="showUpload" :allow-multiple="allowMultiple" />
    </v-main>
  </v-app>
</template>
<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcNewSubmission from '../AcNewSubmission.vue'
import Subjective from '@/mixins/subjective'
import Upload from '@/mixins/upload'
import {Prop} from 'vue-property-decorator'
  @Component({
    components: {AcNewSubmission},
  })
export default class DummySubmit extends mixins(Subjective, Upload) {
  @Prop({default: false})
  public allowMultiple!: boolean
  public created() {
    this.showUpload = true
  }
}
</script>
