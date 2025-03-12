<template>
  <v-card-text class="registration-page">
    <ac-form @submit.prevent="registerForm.submitThen(loginHandler)">
      <ac-form-container
        :sending="loginForm.sending"
        :errors="loginForm.errors"
      >
        <ac-bound-field
          label="Username"
          placeholder=""
          :field="registerForm.fields.username"
          hint="You can change this later."
        />
        <ac-bound-field
          label="Email"
          placeholder="test@example.com"
          :field="registerForm.fields.email"
        />
        <ac-bound-field
          label="Password"
          type="password"
          :field="registerForm.fields.password"
        />
        <ac-bound-field
          label="Promo Code"
          placeholder=""
          :field="registerForm.fields.registration_code"
          hint="If you've been given a promo code, please enter it here!"
          prepend-icon="mdi-tag"
        />
        <v-row>
          <v-col cols="12" sm="6">
            <ac-bound-field
              label="Keep Me up to Date"
              hint="Keep up to date with the latest news on Artconomy using our mailing list"
              :field="registerForm.fields.mail"
              field-type="ac-checkbox"
              :persistent-hint="true"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <ac-bound-field
              label="I'm an artist!"
              hint="Enable artist tools in your account. You can change this later."
              :field="registerForm.fields.artist_mode"
              field-type="ac-checkbox"
              :persistent-hint="true"
            />
          </v-col>
        </v-row>
        <v-input v-bind="registerForm.fields.recaptcha.bind" class="mt-4">
          <v-col class="text-center">
            <div style="display: inline-block">
              <vue-hcaptcha
                ref="recaptcha"
                :sitekey="siteKey"
                theme="dark"
                @verify="registerForm.fields.recaptcha.update"
                @expired="registerForm.fields.recaptcha.update('')"
              />
            </div>
          </v-col>
        </v-input>
        <p>
          By Registering, you are agreeing to be bound by Artconomy's
          <router-link :to="{ name: 'TermsOfService' }">
            Terms of Service
          </router-link>
          and
          <router-link :to="{ name: 'PrivacyPolicy' }">
            Privacy Policy
          </router-link>
          .
        </p>
        <v-btn
          id="registerSubmit"
          color="primary"
          type="submit"
          variant="flat"
          :disabled="registerForm.disabled"
        >
          Register
        </v-btn>
      </ac-form-container>
    </ac-form>
  </v-card-text>
</template>

<script setup lang="ts">
import { useAuth } from "@/components/views/auth/mixins/Auth.ts"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import VueHcaptcha from "@/components/fields/hcaptcha/VueHcaptcha.vue"
import { computed, ref, watch } from "vue"

const siteKey = computed(() => window.RECAPTCHA_SITE_KEY || "undefined")
const { registerForm, loginForm, loginHandler } = useAuth()
const recaptcha = ref<null | typeof VueHcaptcha>()
watch(
  () => registerForm.sending,
  (newVal, oldVal) => {
    if (oldVal && !newVal) {
      recaptcha.value?.reset()
      registerForm.fields.recaptcha.update("", false)
    }
  },
)
</script>

<style scoped></style>
