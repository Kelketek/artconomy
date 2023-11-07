<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="8" md="6" offset-sm="2" offset-md="3" class="text-center">
        <v-tabs class="inverse" fixed-tabs>
          <v-tab :to="{name: 'Login', query: {...$route.query}}" :replace="true">
            Login
          </v-tab>
          <v-tab :to="{name: 'Register', query: {...$route.query}}" :replace="true">
            Register
          </v-tab>
          <v-tab :to="{name: 'Forgot', query: {...$route.query}}" :replace="true">
            Forgot
          </v-tab>
        </v-tabs>
        <router-view ref="currentView"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import VueHcaptcha from '@hcaptcha/vue3-hcaptcha'
import Viewer from '@/mixins/viewer'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {Auth} from '@/components/views/auth/mixins/Auth'
import {watch} from 'vue'

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
  components: {
    AcBoundField,
    AcForm,
    AcFormContainer,
    VueHcaptcha,
  },
})
class AuthViews extends mixins(Viewer, Auth) {
  public created() {
    watch(() => this.loginForm.fields.email.value, syncTo(['registerForm', 'email'], ['forgotForm', 'email']).bind(this))
    watch(() => this.registerForm.fields.email.value, syncTo(['loginForm', 'email'], ['forgotForm', 'email']).bind(this))
    watch(() => this.forgotForm.fields.email.value, syncTo(['loginForm', 'email'], ['registerForm', 'email']).bind(this))
    watch(() => this.loginForm.fields.password.value, syncTo(['registerForm', 'password']).bind(this))
    watch(() => this.registerForm.fields.password.value, syncTo(['loginForm', 'password']).bind(this))
    watch(() => this.loginForm.fields.order_claim.value, syncTo(['registerForm', 'order_claim']).bind(this))
    watch(() => this.registerForm.fields.order_claim.value, syncTo(['loginForm', 'order_claim']).bind(this))
    this.loginForm.fields.order_claim.update(this.$route.query.claim || '', false)
    this.registerForm.fields.artist_mode.update(((this.$route.query.artist_mode && true) || false), false)
    this.loginForm.clearErrors()
    this.registerForm.clearErrors()
  }
}

export default toNative(AuthViews)
</script>
