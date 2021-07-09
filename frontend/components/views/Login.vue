<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="8" md="6" offset-sm="2" offset-md="3" class="text-center">
        <v-tabs class="inverse" v-model="loginTab" fixed-tabs>
          <v-tab href="#tab-login" id="set-login">
            Login
          </v-tab>
          <v-tab href="#tab-register" id="set-register">
            Register
          </v-tab>
          <v-tab href="#tab-forgot" id="set-forgot">
            Forgot
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="loginTab">
          <v-tab-item value="tab-login">
            <v-card-text>
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
                             :disabled="loginForm.disabled">
                        Login
                      </v-btn>
                    </v-col>
                  </v-row>
                </ac-form-container>
              </ac-form>
            </v-card-text>
          </v-tab-item>
          <v-tab-item value="tab-register">
            <v-card-text>
              <ac-form @submit.prevent="registerForm.submitThen(loginHandler)">
                <ac-form-container :sending="loginForm.sending" :errors="loginForm.errors">
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
                      prepend-icon="local_offer"
                  />
                  <v-row>
                    <v-col cols="12" sm="6" >
                      <ac-bound-field
                        label="Keep Me up to Date"
                        hint="Keep up to date with the latest news on Artconomy using our mailing list"
                        :field="registerForm.fields.mail"
                        field-type="ac-checkbox"
                        :persistent-hint="true"
                      />
                    </v-col>
                    <v-col cols="12" sm="6" >
                      <ac-bound-field
                        label="I'm an artist!"
                        hint="Enable artist tools in your account. You can change this later."
                        :field="registerForm.fields.artist_mode"
                        field-type="ac-checkbox"
                        :persistent-hint="true"
                      >
                      </ac-bound-field>
                    </v-col>
                  </v-row>
                  <v-input v-bind="registerForm.fields.recaptcha.bind" class="mt-4">
                    <v-col class="text-center" >
                      <div style="display: inline-block">
                        <vue-hcaptcha
                            :sitekey="siteKey"
                            ref="recaptcha"
                            @verify="registerForm.fields.recaptcha.update"
                            @expired="registerForm.fields.recaptcha.update('')"
                            theme="dark"
                        />
                      </div>
                    </v-col>
                  </v-input>
                  <p>
                    By Registering, you are agreeing to be bound by Artconomy's
                    <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
                    and
                    <router-link :to="{name: 'PrivacyPolicy'}">Privacy Policy</router-link>
                    .
                  </p>
                  <v-btn color="primary" id="registerSubmit" type="submit"
                         :disabled="registerForm.disabled">
                    Register
                  </v-btn>
                </ac-form-container>
              </ac-form>
            </v-card-text>
          </v-tab-item>
          <v-tab-item value="tab-forgot">
            <v-card-text>
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
                         type="submit">
                    Reset
                  </v-btn>
                </ac-form-container>
              </ac-form>
            </v-card-text>
          </v-tab-item>
        </v-tabs-items>
        <div>
        </div>
        <v-dialog
            @keydown.enter="sendLogin()"
            v-model="showTokenPrompt"
            width="500"
        >
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
                      v-mask="'### ###'"
                      :field="loginForm.fields.token"
                      :autofocus="true"
                      id="field-token"
                  />
                  <div class="text-center">
                    <v-btn @click="showTokenPrompt = false">Cancel</v-btn>
                    <v-btn color="primary" id="tokenSubmit" type="submit"
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
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {isAxiosError, paramHandleMap, singleQ} from '@/lib/lib'
import Component, {mixins} from 'vue-class-component'
import {State} from 'vuex-class'
import {FormController} from '@/store/forms/form-controller'
import {Watch} from 'vue-property-decorator'
import AcFormContainer from '../wrappers/AcFormContainer.vue'
import {AxiosError, AxiosResponse} from 'axios'
import VueHcaptcha from '@hcaptcha/vue-hcaptcha'
import {UserStoreState} from '@/store/profiles/types/UserStoreState'
import Viewer from '../../mixins/viewer'
import {User} from '@/store/profiles/types/User'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {mask} from 'vue-the-mask'

declare type SyncFunc = (value: any) => void

function syncTo(...fields: Array<[string, string]>): SyncFunc {
  function syncedField(this: any, value: any): void {
    for (const field of fields) {
      const formName = field[0]
      const fieldName = field[1]
      /* istanbul ignore if */
      if (!this[formName]) {
        // Form isn't (yet) defined, can't sync.
        return
      }
      this[formName].fields[fieldName].update(value, false)
    }
  }

  return syncedField
}

@Component({
  name: 'Login',
  components: {AcBoundField, AcForm, AcFormContainer, VueHcaptcha},
  directives: {mask},
})
export default class Login extends mixins(Viewer) {
    @State('profiles') private profiles!: UserStoreState
    @paramHandleMap('tabName') private loginTab!: string
    private loginForm: FormController | null = null
    private registerForm: FormController | null = null
    private forgotForm: FormController | null = null
    private resetSent: boolean = false
    private showTokenPrompt: boolean = false
    // @ts-ignore
    @Watch('loginForm.fields.email.value')
    private loginEmailSync = syncTo(['registerForm', 'email'], ['forgotForm', 'email'])

    // @ts-ignore
    @Watch('registerForm.fields.email.value')
    private registerEmailSync = syncTo(['loginForm', 'email'], ['forgotForm', 'email'])

    // @ts-ignore
    @Watch('forgotForm.fields.email.value')
    private forgotEmailSync = syncTo(['loginForm', 'email'], ['registerForm', 'email'])

    // @ts-ignore
    @Watch('loginForm.fields.password.value')
    private loginPasswordSync = syncTo(['registerForm', 'password'])

    // @ts-ignore
    @Watch('registerForm.fields.password.value')
    private registerPasswordSync = syncTo(['loginForm', 'password'])

    // @ts-ignore
    @Watch('loginForm.fields.order_claim.value')
    private loginOrderClaimSync = syncTo(['registerForm', 'order_claim'])

    // @ts-ignore
    @Watch('registerForm.fields.order_claim.value')
    private registerOrderClaimSync = syncTo(['loginForm', 'order_claim'])

    public created() {
      this.loginForm = this.$getForm('login', {
        endpoint: '/api/profiles/v1/login/',
        fields: {
          email: {value: '', validators: [{name: 'email'}, {name: 'required'}]},
          password: {value: '', validators: [{name: 'required'}]},
          token: {value: ''},
          order_claim: {value: '', omitIf: ''},
        },
      })
      this.registerForm = this.$getForm('register', {
        endpoint: '/api/profiles/v1/register/',
        fields: {
          username: {value: '', validators: [{name: 'username', async: true}]},
          email: {
            value: '',
            validators: [
              {name: 'email', async: true},
            ],
          },
          password: {value: '', validators: [{name: 'required'}, {name: 'password', async: true}]},
          recaptcha: {value: '', validators: [{name: 'required'}]},
          artist_mode: {value: false},
          registration_code: {value: ''},
          mail: {value: true},
          order_claim: {value: '', omitIf: ''},
        },
      })
      this.forgotForm = this.$getForm('forgot', {
        endpoint: '/api/profiles/v1/forgot-password/',
        fields: {
          email: {value: '', validators: [{name: 'required'}]},
        },
      })
      this.loginForm.fields.order_claim.update(this.$route.query.claim || '', false)
      this.registerForm.fields.artist_mode.update(((this.$route.query.artist_mode && true) || false), false)
      this.loginForm.clearErrors()
      this.registerForm.clearErrors()
    }

    private loginHandler(response: User) {
      this.viewerHandler.user.x = response
      if ('next' in this.$route.query) {
        if (singleQ(this.$route.query.next) === '/') {
          this.$router.push({name: 'Profile', params: {username: response.username}})
          return
        }
        this.$router.push(singleQ(this.$route.query.next))
      } else if (this.loginTab === 'tab-register') {
        this.sendToProfile()
      } else {
        this.$router.push({name: 'Home'})
      }
    }

    private sendToProfile() {
      this.$router.push(
        {name: 'Profile', params: {username: (this.viewer as User).username}, query: {editing: 'true'}},
      )
    }

    private loginFailure(error: AxiosError) {
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

    // noinspection JSUnusedLocalSymbols
    private forgotHandler(): void {
      this.resetSent = true
      this.showTokenPrompt = false
    }

    // noinspection JSUnusedLocalSymbols,JSMethodCanBeStatic
    private get siteKey() {
      return window.RECAPTCHA_SITE_KEY
    }

    // noinspection JSUnusedLocalSymbols
    private sendLogin() {
      (this.loginForm as FormController).submitThen(this.loginHandler, this.loginFailure).then()
    }

    @Watch('registerForm.sending')
    private resetCaptcha(newVal: string, oldVal: string) {
      if (oldVal && !newVal) {
        (this.$refs.recaptcha as any).reset();
        (this.registerForm as FormController).fields.recaptcha.update('', false)
      }
    }

    @Watch('showTokenPrompt')
    private focusToken(newVal: boolean) {
      if (newVal) {
        this.$nextTick(() => {
          const element = document.getElementById('field-token');
          (element as HTMLElement).focus()
        })
      }
    }
}
</script>
