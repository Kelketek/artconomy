<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="8" md="6" offset-sm="2" offset-md="3" class="text-center">
        <v-tabs class="inverse" fixed-tabs>
          <v-tab :to="{name: 'Login', query: {...route.query}}" :replace="true">
            Login
          </v-tab>
          <v-tab :to="{name: 'Register', query: {...route.query}}" :replace="true">
            Register
          </v-tab>
          <v-tab :to="{name: 'Forgot', query: {...route.query}}" :replace="true">
            Forgot
          </v-tab>
        </v-tabs>
        <router-view ref="currentView"/>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {useAuth} from '@/components/views/auth/mixins/Auth.ts'
import {watch} from 'vue'
import {useRoute} from 'vue-router'
import {useViewer} from '@/mixins/viewer.ts'

declare type SyncFunc = (value: any) => void
declare type AuthType = Omit<ReturnType<typeof useAuth>, 'loginHandler'|'sendToProfile'>

const route = useRoute()
const forms = useAuth()

const syncTo = (...fields: Array<[keyof AuthType, string]>): SyncFunc => {
  return (value: keyof ReturnType<typeof useAuth>): void => {
    for (const field of fields) {
      const formName = field[0]
      const fieldName = field[1]
      /* istanbul ignore if */
      if (!forms[formName]) {
        // Form isn't (yet) defined, can't sync.
        return
      }
      forms[formName].fields[fieldName].update(value, false)
    }
  }
}


watch(() => forms.loginForm.fields.email.value, syncTo(['registerForm', 'email'], ['forgotForm', 'email']))
watch(() => forms.registerForm.fields.email.value, syncTo(['loginForm', 'email'], ['forgotForm', 'email']))
watch(() => forms.forgotForm.fields.email.value, syncTo(['loginForm', 'email'], ['registerForm', 'email']))
watch(() => forms.loginForm.fields.password.value, syncTo(['registerForm', 'password']))
watch(() => forms.registerForm.fields.password.value, syncTo(['loginForm', 'password']))
watch(() => forms.loginForm.fields.order_claim.value, syncTo(['registerForm', 'order_claim']))
watch(() => forms.registerForm.fields.order_claim.value, syncTo(['loginForm', 'order_claim']))
forms.loginForm.fields.order_claim.update(route.query.claim || '', false)
forms.registerForm.fields.artist_mode.update(((route.query.artist_mode && true) || false), false)
forms.loginForm.clearErrors()
forms.registerForm.clearErrors()
// Used by tests.
const {viewer} = useViewer()
defineExpose({viewer})
</script>
