<template>
  <v-card-text class="login-page">
    <ac-form @submit.prevent="sendLogin()">
      <ac-form-container :sending="loginForm.sending" :errors="loginForm.errors">
        <v-row>
          <v-col cols="12">
            <ac-bound-field
                label="Email"
                placeholder="test@example.com"
                :field="loginForm.fields.email"
            />
          </v-col>
          <v-col cols="12">
            <ac-bound-field
                label="Password"
                type="password"
                :field="loginForm.fields.password"
            />
          </v-col>
          <v-col cols="12">
            <v-btn color="primary" id="loginSubmit" type="submit"
                   variant="flat"
                   :disabled="loginForm.disabled">
              Login
            </v-btn>
          </v-col>
        </v-row>
      </ac-form-container>
    </ac-form>
    <v-dialog
        @keydown.enter="sendLogin()"
        v-model="showTokenPrompt"
        width="500"
        :attach="$modalTarget"
    >
      <span v-if="showTokenPrompt" class="token-prompt-loaded"/>
      <v-card>
        <ac-form @submit.prevent="sendLogin()">
          <v-card-text>
            <p>
              This account is protected by Two Factor Authentication. Please use your
              authentication device to generate a login token, or check your Telegram messages if you've set
              up Telegram 2FA.
            </p>
            <p>If you have lost your 2FA device/service, please contact support@artconomy.com with the subject 'Lost
              2FA'.</p>
            <ac-form-container :sending="loginForm.sending" :errors="loginForm.errors">
              <ac-bound-field
                  label="Token"
                  v-mask-token
                  :field="loginForm.fields.token"
                  :autofocus="true"
                  id="field-token"
              />
              <div class="text-center">
                <v-btn @click="showTokenPrompt = false">Cancel</v-btn>
                <v-btn color="primary" id="tokenSubmit" type="submit"
                       variant="flat"
                       :disabled="loginForm.disabled"
                >
                  Verify
                </v-btn>
              </div>
            </ac-form-container>
          </v-card-text>
        </ac-form>
      </v-card>
    </v-dialog>
  </v-card-text>
</template>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import {Auth} from '@/components/views/auth/mixins/Auth.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import {AxiosResponse} from 'axios'
import {isAxiosError} from '@/lib/lib.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import Viewer from '@/mixins/viewer.ts'
import {AcServerError} from '@/types/AcServerError.ts'
import {vMaskToken as MaskToken} from '@/lib/vMask.ts'

@Component({
  components: {
    AcBoundField,
    AcFormContainer,
    AcForm,
  },
  directives: {
    MaskToken,
  }
})
class Login extends mixins(Auth, Viewer) {
  public showTokenPrompt: boolean = false

  @Watch('showTokenPrompt')
  public focusToken(newVal: boolean) {
    if (newVal) {
      this.$nextTick(() => {
        const element = document.getElementById('field-token');
        (element as HTMLElement).focus()
      })
    }
  }

  public loginFailure(error: AcServerError) {
    const loginForm = (this.loginForm as FormController)
    if (!isAxiosError(error)) {
      loginForm.setErrors(error)
      return
    }
    if (!(error.response as AxiosResponse).data) {
      loginForm.setErrors(error)
      return
    }
    if (('token' in (error.response as AxiosResponse).data)) {
      const tokenErrors = (error.response as AxiosResponse).data.token
      if (!tokenErrors.length) {
        loginForm.setErrors(error)
        return
      }
      if (this.showTokenPrompt) {
        loginForm.setErrors(error)
        return
      }
      loginForm.sending = false
      this.showTokenPrompt = true
      return
    }
    loginForm.setErrors(error)
  }

  public sendLogin() {
    (this.loginForm as FormController).submitThen(this.loginHandler, this.loginFailure).then()
  }
}

export default toNative(Login)
</script>

<style scoped>

</style>
