<template>
  <v-card-text class="login-page">
    <ac-form @submit.prevent="sendLogin()">
      <ac-form-container
        :sending="loginForm.sending"
        :errors="loginForm.errors"
      >
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
            <v-btn
              id="loginSubmit"
              color="primary"
              type="submit"
              variant="flat"
              :disabled="loginForm.disabled"
            >
              Login
            </v-btn>
          </v-col>
        </v-row>
      </ac-form-container>
    </ac-form>
    <v-dialog
      v-model="showTokenPrompt"
      width="500"
      :attach="modalTarget"
      class="token-prompt-dialog"
      @keydown.enter="sendLogin()"
    >
      <v-col v-if="showTokenPrompt" class="token-prompt-loaded" />
      <v-card>
        <ac-form @submit.prevent="sendLogin()">
          <v-card-text>
            <p>
              This account is protected by Two Factor Authentication. Please use
              your authentication device to generate a login token, or check
              your Telegram messages if you've set up Telegram 2FA.
            </p>
            <p>
              If you have lost your 2FA device/service, please contact
              support@artconomy.com with the subject 'Lost 2FA'.
            </p>
            <ac-form-container
              :sending="loginForm.sending"
              :errors="loginForm.errors"
            >
              <ac-bound-field
                id="field-token"
                v-mask-token
                label="Token"
                :field="loginForm.fields.token"
                :autofocus="true"
              />
              <div class="text-center">
                <v-btn @click="showTokenPrompt = false"> Cancel </v-btn>
                <v-btn
                  id="tokenSubmit"
                  color="primary"
                  type="submit"
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

<script setup lang="ts">
import { useAuth } from "@/components/views/auth/mixins/Auth.ts"
import { AxiosResponse } from "axios"
import { isAxiosError } from "@/lib/lib.ts"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcForm from "@/components/wrappers/AcForm.vue"
import { vMaskToken } from "@/lib/vMask.ts"
import { useTargets } from "@/plugins/targets.ts"
import { nextTick, ref, watch } from "vue"
import type { AcServerError } from "@/types/main"

const { loginForm, loginHandler } = useAuth()
const { modalTarget } = useTargets()
const showTokenPrompt = ref(false)

const loginFailure = (error: AcServerError) => {
  if (!isAxiosError(error)) {
    loginForm.setErrors(error)
    return
  }
  if (!(error.response as AxiosResponse).data) {
    loginForm.setErrors(error)
    return
  }
  if ("token" in (error.response as AxiosResponse).data) {
    const tokenErrors = (error.response as AxiosResponse).data.token
    if (!tokenErrors.length) {
      loginForm.setErrors(error)
      return
    }
    if (showTokenPrompt.value) {
      loginForm.setErrors(error)
      return
    }
    loginForm.sending = false
    showTokenPrompt.value = true
    return
  }
  loginForm.setErrors(error)
}

const sendLogin = () => {
  loginForm.submitThen(loginHandler, loginFailure).then()
}

watch(showTokenPrompt, (newVal) => {
  if (newVal) {
    nextTick(() => {
      document.getElementById("field-token")?.focus()
    })
  }
})
</script>

<style scoped></style>
