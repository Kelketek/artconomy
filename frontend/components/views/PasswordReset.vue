<template>
  <ac-load-section :controller="validator">
    <template v-slot:default>
      <v-row no-gutters   class="mt-5">
        <v-col class="text-center" cols="12" md="6" offset-md="3" >
          <ac-form @submit.prevent="resetForm.submitThen(postReset)">
            <ac-form-container class="mt-3" :sending="resetForm.sending" :errors="resetForm.errors" v-if="validator.x">
              <v-row no-gutters  >
                <v-col cols="12">
                  <p>Reset password for {{username}}</p>
                </v-col>
                <v-col cols="12">
                  <ac-bound-field
                      :field="resetForm.fields.new_password" type="password"
                      label="New Password"
                  ></ac-bound-field>
                </v-col>
                <v-col cols="12">
                  <ac-bound-field
                      :field="resetForm.fields.new_password2" type="password"
                      label="New Password (again)"
                  ></ac-bound-field>
                </v-col>
                <v-col class="text-center" cols="12" >
                  <v-btn type="submit" color="primary">Reset Password</v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </ac-form>
        </v-col>
      </v-row>
    </template>
    <template v-slot:failure>
      <v-container>
        <v-row no-gutters  >
          <v-col class="text-center" cols="12" md="6" offset-md="3" >
            <v-alert value="error" type="error">
              Your reset token is invalid or has expired.
              <router-link :to="{name: 'Login', params: {tabName: 'forgot'}}">You can request a new one here!</router-link>
            </v-alert>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '../wrappers/AcLoadSection.vue'
import {Prop} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {User} from '@/store/profiles/types/User'
import Viewer from '@/mixins/viewer'
import AcBoundField from '@/components/fields/AcBoundField'
import {SingleController} from '@/store/singles/controller'
import AcForm from '@/components/wrappers/AcForm.vue'
  @Component({
    components: {AcForm, AcBoundField, AcFormContainer, AcLoadSection},
  })
export default class PasswordReset extends mixins(Viewer) {
    public resetForm: FormController = null as unknown as FormController
    public validator: SingleController<any> = null as unknown as SingleController<any>
    @Prop({required: true})
    public resetToken!: string

    @Prop({required: true})
    public username!: string

    public postReset(response: User) {
      this.viewerHandler.user.x = response
      this.$router.push(
        {name: 'Profile', params: {username: (this.viewer as User).username}, query: {editing: 'true'}},
      )
    }

    public created() {
      this.validator = this.$getSingle(
        'passwordToken', {
          endpoint: `/api/profiles/forgot-password/token-check/${this.username}/${this.resetToken}/`,
        },
      )
      this.validator.get()
      this.resetForm = this.$getForm(
        'passwordReset', {
          endpoint: `/api/profiles/forgot-password/perform-reset/${this.username}/${this.resetToken}/`,
          fields: {
            new_password: {value: ''},
            new_password2: {
              value: '',
              validators: [{
                name: 'matches', args: ['new_password', 'Passwords do not match.'],
              }],
            },
          },
        },
      )
    }
}
</script>
