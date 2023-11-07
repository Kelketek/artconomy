<template>
  <v-card-text class="forgot-page">
    <p>Enter your username or email address below, and we will send you a link to reset your password.</p>
    <ac-form @submit.prevent="forgotForm.submitThen(forgotHandler)">
      <ac-form-container v-bind="forgotForm.bind">
        <ac-bound-field
            label="Email or Username"
            :field="forgotForm.fields.email"
        />
        <v-alert type="info" v-model="resetSent" dismissible>
          Email sent! Please check your inbox (and your spam folder)!
        </v-alert>
        <v-btn color="primary" id="forgotSubmit"
               class="mb-2"
               variant="flat"
               type="submit">
          Reset
        </v-btn>
      </ac-form-container>
    </ac-form>
  </v-card-text>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer'
import {Auth} from '@/components/views/auth/mixins/Auth'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcBoundField from '@/components/fields/AcBoundField'

@Component({
  components: {
    AcFormContainer,
    AcForm,
    AcBoundField,
  },
})
class Forgot extends mixins(Auth, Viewer) {
  public resetSent: boolean = false

  public forgotHandler(): void {
    this.resetSent = true
  }
}

export default toNative(Forgot)
</script>

<style scoped>

</style>
