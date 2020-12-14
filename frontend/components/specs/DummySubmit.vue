<template>
  <v-app>
    <v-main>
      <ac-new-submission ref="submissionForm" title="Sharable thing!" :username="username" v-model="showUpload"></ac-new-submission>
    </v-main>
  </v-app>
</template>
<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcNewSubmission from '../AcNewSubmission.vue'
import Subjective from '@/mixins/subjective'
import Upload from '@/mixins/upload'
  @Component({
    components: {AcNewSubmission},
  })
export default class DummySubmit extends mixins(Subjective, Upload) {
  public created() {
    this.showUpload = true
  }
}
</script>
