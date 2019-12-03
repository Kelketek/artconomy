<template>
  <ac-load-section :controller="validator">
    <template v-slot:default>
      <v-layout row wrap class="mt-5">
        <v-flex xs12 md6 offset-md3 text-xs-center>
          <ac-form @submit.prevent="resetForm.submitThen(postReset)">
            <ac-form-container class="mt-3" :sending="resetForm.sending" :errors="resetForm.errors" v-if="validator.x">
              <v-layout row wrap>
                <v-flex xs12>
                  <p>Reset password for {{username}}</p>
                </v-flex>
                <v-flex xs12>
                  <ac-bound-field
                      :field="resetForm.fields.new_password" type="password"
                      label="New Password"
                  ></ac-bound-field>
                </v-flex>
                <v-flex xs12>
                  <ac-bound-field
                      :field="resetForm.fields.new_password2" type="password"
                      label="New Password (again)"
                  ></ac-bound-field>
                </v-flex>
                <v-flex xs12 text-xs-center>
                  <v-btn type="submit" color="primary">Reset Password</v-btn>
                </v-flex>
              </v-layout>
            </ac-form-container>
          </ac-form>
        </v-flex>
      </v-layout>
    </template>
    <template v-slot:failure>
      <v-container>
        <v-layout row wrap>
          <v-flex xs12 md6 offset-md3 text-xs-center>
            <v-alert value="error" type="error">
              Your reset token is invalid or has expired.
              <router-link :to="{name: 'Login', params: {tabName: 'forgot'}}">You can request a new one here!</router-link>
            </v-alert>
          </v-flex>
        </v-layout>
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
        {name: 'Profile', params: {username: (this.viewer as User).username}, query: {editing: 'true'}}
      )
    }
    public created() {
      this.validator = this.$getSingle(
        'passwordToken', {
          endpoint: `/api/profiles/v1/forgot-password/token-check/${this.username}/${this.resetToken}/`,
        }
      )
      this.validator.get()
      this.resetForm = this.$getForm(
        'passwordReset', {
          endpoint: `/api/profiles/v1/forgot-password/perform-reset/${this.username}/${this.resetToken}/`,
          fields: {
            new_password: {value: ''},
            new_password2: {value: '',
              validators: [{
                name: 'matches', args: ['new_password', 'Passwords do not match.'],
              }]},
          },
        }
      )
    }
}
</script>
